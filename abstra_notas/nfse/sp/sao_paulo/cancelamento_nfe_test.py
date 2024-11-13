from unittest import TestCase
from .cancelamento_nfe import CancelamentoNFe, RetornoCancelamentoNFe
from pathlib import Path
from lxml.etree import fromstring
from .cliente import ClienteMock
from abstra_notas.assinatura import AssinadorMock
from abstra_notas.validacoes.xml_iguais import assert_xml_iguais


class CancelamentoTest(TestCase):
    def test_exemplo(self):
        assinador = AssinadorMock()
        self.maxDiff = None
        exemplo_path = Path(__file__).parent / "exemplos" / "PedidoCancelamentoNFe.xml"
        exemplo_xml = assinador.assinar_xml(fromstring(exemplo_path.read_bytes()))

        pedido = CancelamentoNFe(
            inscricao_prestador="39616924",
            numero_nfe="17945",
            remetente="99-99/999.70-00//100",
            transacao=True,
        )

        pedido_xml = assinador.assinar_xml(pedido.gerar_xml(assinador=assinador))
        assert_xml_iguais(
            pedido_xml,
            exemplo_xml,
            ignorar_tags=["AssinaturaCancelamento", "Signature"],
        )

        cliente = ClienteMock()
        resultado = cliente.cancelar_nota(pedido)

        self.assertEqual(
            resultado,
            RetornoCancelamentoNFe(),
        )
