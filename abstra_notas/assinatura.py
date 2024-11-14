from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization.pkcs12 import (
    load_key_and_certificates,
)
from cryptography.hazmat.backends import default_backend
from pathlib import Path
from tempfile import NamedTemporaryFile
from lxml.etree import tostring, fromstring, ElementBase
import xmlsec


class Assinador:
    pfx_path: Path
    pfx_password: str
    cert_pem_bytes: bytes
    private_key_pem_bytes: bytes

    def __init__(
        self,
        pfx_path: Path,
        pfx_password: str,
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

    def assinar_xml(self, element: ElementBase) -> ElementBase:
        element = fromstring(tostring(element, encoding=str))
        key = xmlsec.Key.from_memory(
            self.private_key_pem_bytes,
            format=xmlsec.constants.KeyDataFormatPem,
            password=self.pfx_password,
        )
        signature_node: ElementBase = xmlsec.template.create(
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
        ctx.key.load_cert_from_memory(
            self.cert_pem_bytes, xmlsec.constants.KeyDataFormatPem
        )
        ctx.sign(signature_node)
        return element

    def assinar_bytes_rsa_sh1(self, data: bytes) -> bytes:
        private_key = serialization.load_pem_private_key(
            self.private_key_pem_bytes,
            password=None,
            backend=default_backend(),
        )

        signature = private_key.sign(
            data,
            padding.PKCS1v15(),
            hashes.SHA1(),
        )
        return signature


class AssinadorMock:
    def assinar_xml(self, element: ElementBase) -> ElementBase:
        signature = """
        <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
            <SignedInfo>
                <CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315" />
                <SignatureMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315" />
                <Reference>
                    <Transforms>
                        <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature" />
                    </Transforms>
                    <DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature" />
                    <DigestValue />
                </Reference>
            </SignedInfo>
            <SignatureValue />
            <KeyInfo>
                <X509Data>
                    <X509Certificate />
                </X509Data>
            </KeyInfo>
        </Signature>
        """
        element.append(fromstring(signature))
        return element

    def assinar_bytes_rsa_sh1(self, data: bytes) -> bytes:
        return data
