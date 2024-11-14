from unittest import TestCase
from .consulta import ConsultaNFePeriodo
from .cliente import ClienteMock
from abstra_notas.assinatura import AssinadorMock
from datetime import date


class ConsultaTest(TestCase):
    def test_recebidas(self):
        assinador = AssinadorMock()
        self.maxDiff = None

        pedido = ConsultaNFePeriodo(
            remetente="75.551.583/0001-48",
            data_fim=date(2015, 1, 28),
            data_inicio=date(2015, 1, 28),
            pagina=1,
            recebidas_por="04.151.050/0001-20",
        )

        assinador.assinar_xml(pedido.gerar_xml(assinador=assinador))

        cliente = ClienteMock()
        cliente.consultar_notas_periodo(pedido)

    def test_emitidas(self):
        assinador = AssinadorMock()
        self.maxDiff = None

        pedido = ConsultaNFePeriodo(
            remetente="75.551.583/0001-48",
            data_fim=date(2015, 1, 28),
            data_inicio=date(2015, 1, 28),
            pagina=1,
            inscricao_municipal="12345678",
        )

        assinador.assinar_xml(pedido.gerar_xml(assinador=assinador))

        cliente = ClienteMock()
        cliente.consultar_notas_periodo(pedido)
