from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
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
from lxml.etree import Element, tostring, fromstring
import xmlsec
import datetime


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

    def assinar_xml(self, element: Element) -> Element:
        element = fromstring(tostring(element, encoding=str))
        key = xmlsec.Key.from_memory(
            self.private_key_pem_bytes,
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
    def assinar_xml(self, element: Element) -> Element:
        return element

    def assinar_bytes_rsa_sh1(self, data: bytes) -> bytes:
        return data
