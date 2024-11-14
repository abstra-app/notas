from unittest import TestCase
from .consulta_cnpj import ConsultaCNPJ, RetornoConsultaCNPJ
from pathlib import Path
from lxml.etree import fromstring
from .cliente import ClienteMock
from abstra_notas.assinatura import AssinadorMock
from abstra_notas.validacoes.xml_iguais import assert_xml_iguais


class ConsultaTest(TestCase):
    def test_exemplo(self):
        assinador = AssinadorMock()
        self.maxDiff = None
        exemplo_path = Path(__file__).parent / "exemplos" / "PedidoConsultaCNPJ.xml"
        exemplo_xml = assinador.assinar_xml(fromstring(exemplo_path.read_bytes()))

        pedido = ConsultaCNPJ(
            contribuinte="99-99/999.70-00//100",
            remetente="99999997000100",
        )

        pedido_xml = assinador.assinar_xml(pedido.gerar_xml(assinador=assinador))
        assert_xml_iguais(
            pedido_xml, exemplo_xml, ignorar_tags=["Assinatura", "Signature"]
        )

        cliente = ClienteMock()
        resultado = cliente.consultar_cnpj(pedido)

        self.assertEqual(
            resultado,
            RetornoConsultaCNPJ(
                emite_nfe=True,
                inscricao_municipal="39616924",
            ),
        )
