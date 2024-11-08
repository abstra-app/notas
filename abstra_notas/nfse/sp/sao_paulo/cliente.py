from ....assinatura import Assinador
from zeep.plugins import HistoryPlugin
from zeep import Client, Transport, Settings
import ssl
from requests import Session
from .pedido import Pedido
from lxml.etree import tostring
from pathlib import Path
from tempfile import mktemp
from .retorno import Retorno


class Cliente:
    assinador: Assinador

    def __init__(self, caminho_pfx: Path, senha_pfx: str):
        self.assinador = Assinador(caminho_pfx, senha_pfx)

    def executar(self, pedido: Pedido) -> Retorno:
        try:
            history = HistoryPlugin()
            keyfile = Path(mktemp())
            keyfile.write_bytes(self.assinador.private_key_pem_bytes)
            certfile = Path(mktemp())
            certfile.write_bytes(self.assinador.cert_pem_bytes)
            url = "https://nfe.prefeitura.sp.gov.br/ws/lotenfe.asmx?WSDL"
            xml = pedido.gerar_xml(self.assinador)
            session = Session()
            session.cert = (certfile, keyfile)
            settings = Settings(strict=True, xml_huge_tree=True)
            transport = Transport(session=session, cache=None)
            client = Client(url, transport=transport,
                            settings=settings, plugins=[history])
            signed_xml = self.assinador.assinar_xml(xml)
            retorno = getattr(client.service, pedido.nome_metodo)(
                1, tostring(signed_xml, encoding=str)
            )
            return pedido.classe_retorno.ler_xml(retorno)
        finally:
            keyfile.unlink()
            certfile.unlink()
