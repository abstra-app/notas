from ....assinatura import Assinador
from zeep import Client, Transport
from requests import Session
from .pedido import Pedido
from lxml.etree import tostring
from pathlib import Path
from .retorno import Retorno


class Cliente:
    assinador: Assinador

    def __init__(self, caminho_pfx: Path, senha_pfx: str):
        self.assinador = Assinador(caminho_pfx, senha_pfx)

    def executar(self, pedido: Pedido) -> Retorno:
        url = "https://nfe.prefeitura.sp.gov.br/ws/lotenfe.asmx?WSDL"
        xml = pedido.gerar_xml(self.assinador)
        with self.assinador.cert_pem_file as cert_pem_file, self.assinador.private_key_pem_file as private_key_pem_file:
            cert = (cert_pem_file.name, private_key_pem_file.name)
            session = Session()
            session.cert = cert
            transport = Transport(session=session, cache=None)
            client = Client(url, transport=transport)
            signed_xml = self.assinador.assinar_xml(xml)

            retorno = getattr(client.service, pedido.__class__.__name__)(
                1, tostring(signed_xml, encoding=str)
            )
            return pedido.classe_retorno.ler_xml(retorno)
