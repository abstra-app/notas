from ....assinatura import Assinador, AssinadorMock
from zeep.plugins import HistoryPlugin
from zeep import Client, Transport, Settings
from requests import Session
from .pedido import Pedido
from lxml.etree import tostring, fromstring, ElementBase
from pathlib import Path
from tempfile import mktemp
from .envio_rps import EnvioRPS, RetornoEnvioRps, EnvioLoteRPS, RetornoEnvioRpsLote
from .consulta_cnpj import ConsultaCNPJ, RetornoConsultaCNPJ
from .cancelamento_nfe import CancelamentoNFe, RetornoCancelamentoNFe
from .consulta import ConsultaNFe, RetornoConsulta, ConsultaNFePeriodo


class Cliente:
    assinador: Assinador

    def __init__(self, caminho_pfx: Path, senha_pfx: str):
        self.assinador = Assinador(caminho_pfx, senha_pfx)

    def executar(self, pedido: Pedido) -> ElementBase:
        try:
            history = HistoryPlugin()
            keyfile = Path(mktemp())
            keyfile.write_bytes(self.assinador.private_key_pem_bytes)
            certfile = Path(mktemp())
            certfile.write_bytes(self.assinador.cert_pem_bytes)
            
            # URL do webservice de NFSe de Fortaleza
            url = "https://nfse.fortaleza.ce.gov.br/WSNacional/nfse.asmx?WSDL"
            
            xml = pedido.gerar_xml(self.assinador)
            session = Session()
            session.cert = (certfile, keyfile)
            settings = Settings(strict=True, xml_huge_tree=True)
            transport = Transport(session=session, cache=None)
            client = Client(
                url, transport=transport, settings=settings, plugins=[history]
            )
            signed_xml = self.assinador.assinar_xml(xml)

            response: str = getattr(client.service, pedido.metodo)(
                tostring(signed_xml, encoding=str)
            )
            
            return fromstring(response.encode("utf-8"))
        finally:
            keyfile.unlink()
            certfile.unlink()

    def gerar_nota(self, pedido: EnvioRPS) -> RetornoEnvioRps:
        return RetornoEnvioRps.ler_xml(self.executar(pedido))

    def gerar_notas_em_lote(self, pedido: EnvioLoteRPS) -> RetornoEnvioRpsLote:
        return RetornoEnvioRpsLote.ler_xml(self.executar(pedido))

    def consultar_cnpj(self, pedido: ConsultaCNPJ) -> RetornoConsultaCNPJ:
        return RetornoConsultaCNPJ.ler_xml(self.executar(pedido))

    def cancelar_nota(self, pedido: CancelamentoNFe) -> RetornoCancelamentoNFe:
        return RetornoCancelamentoNFe.ler_xml(self.executar(pedido))

    def consultar_nota(self, pedido: ConsultaNFe) -> RetornoConsulta:
        return RetornoConsulta.ler_xml(self.executar(pedido))

    def consultar_notas_periodo(self, pedido: ConsultaNFePeriodo) -> RetornoConsulta:
        return RetornoConsulta.ler_xml(self.executar(pedido))


class ClienteMock(Cliente):
    def __init__(self):
        self.assinador = AssinadorMock()

    def executar(self, pedido: Pedido) -> ElementBase:
        # Implementação mock para testes
        xml_mock = """<?xml version="1.0" encoding="UTF-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
                <GerarNfseResposta>
                    <ListaNfse>
                        <CompNfse>
                            <Nfse>
                                <InfNfse>
                                    <Numero>1</Numero>
                                    <CodigoVerificacao>12345678</CodigoVerificacao>
                                    <DataEmissao>2023-01-01</DataEmissao>
                                </InfNfse>
                            </Nfse>
                        </CompNfse>
                    </ListaNfse>
                </GerarNfseResposta>
            </soap:Body>
        </soap:Envelope>"""
        return fromstring(xml_mock.encode("utf-8"))
