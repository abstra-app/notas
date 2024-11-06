from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization.pkcs12 import (
    load_key_and_certificates,
)
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from cryptography import x509
from os import getenv
from pathlib import Path
from tempfile import NamedTemporaryFile
from lxml.etree import Element, tostring, canonicalize, fromstring
import xmlsec
import datetime


class Assinatura:
    pfx_path: Path
    pfx_password: str
    cert_pem_bytes: bytes
    private_key_pem_bytes: bytes

    def __init__(
        self,
        pfx_path: Path = Path(getenv("NFSE_PFX_PATH")),
        pfx_password: str = getenv("NFSE_PFX_PASSWORD"),
    ):
        self.pfx_path = pfx_path
        self.pfx_password = pfx_password

        with open(self.pfx_path, "rb") as f:
            pfx_data = f.read()

        private_key, certificate, _ = load_key_and_certificates(
            pfx_data, self.pfx_password.encode(), backend=default_backend()
        )

        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        cert_pem = certificate.public_bytes(serialization.Encoding.PEM)

        self.cert_pem_bytes = cert_pem
        self.private_key_pem_bytes = private_key_pem

    @property
    def cert_pem_file(self):
        file = NamedTemporaryFile()
        file.write(self.cert_pem_bytes)
        file.seek(0)
        return file

    @property
    def private_key_pem_file(self):
        file = NamedTemporaryFile()
        file.write(self.private_key_pem_bytes)
        file.seek(0)
        return file

    def assinar(self, element: Element) -> Element:
        with self.private_key_pem_file as private_key_pem_file, self.cert_pem_file as cert_pem_file:
            element = fromstring(tostring(element, encoding=str))
            key = xmlsec.Key.from_file(
                private_key_pem_file.name,
                format=xmlsec.constants.KeyDataFormatPem,
                password=self.pfx_password,
            )
            signature_node: Element = xmlsec.template.create(
                element,
                c14n_method=xmlsec.constants.TransformInclC14N,
                sign_method=xmlsec.constants.TransformRsaSha1,
            )
            element.append(signature_node)
            ref = xmlsec.template.add_reference(
                signature_node, xmlsec.constants.TransformSha1, uri=""
            )
            xmlsec.template.add_transform(ref, xmlsec.constants.TransformEnveloped)
            xmlsec.template.add_transform(ref, xmlsec.constants.TransformInclC14N)
            key_info = xmlsec.template.ensure_key_info(signature_node)
            xmlsec.template.add_x509_data(key_info)
            ctx = xmlsec.SignatureContext()
            ctx.key = key
            ctx.key.load_cert_from_file(
                cert_pem_file.name, xmlsec.constants.KeyDataFormatPem
            )
            ctx.sign(signature_node)
            print(tostring(element, encoding=str))
            return element


def gerar_pfx_teste(path: Path, password: str):
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Generate a self-signed certificate
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "My Company"),
            x509.NameAttribute(NameOID.COMMON_NAME, "mycompany.com"),
        ]
    )
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(
            # Certificate valid for 10 days
            datetime.datetime.utcnow()
            + datetime.timedelta(days=10)
        )
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName("localhost")]),
            critical=False,
        )
        .sign(private_key, hashes.SHA256())
    )

    # Serialize private key and certificate to PFX
    pfx = serialization.pkcs12.serialize_key_and_certificates(
        name=b"mykey",
        key=private_key,
        cert=cert,
        cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode()),
    )

    path.write_bytes(pfx)
