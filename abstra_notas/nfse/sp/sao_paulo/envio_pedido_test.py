from unittest import TestCase
from .envio_rps import EnvioRPS
from pathlib import Path
from lxml.etree import XMLSchema, fromstring
from datetime import date
import re
from abstra_notas.assinatura import AssinadorMock
from abstra_notas.validacoes.xml_iguais import assert_xml_iguais


class EnvioTest(TestCase):
    def test_exemplo(self):
        assinador = AssinadorMock()
        self.maxDiff = None
        exemplo_path = Path(__file__).parent / "exemplos" / "PedidoEnvioRPS.xml"
        exemplo_xml = assinador.assinar_xml(
            fromstring(exemplo_path.read_text(encoding="utf-8"))
        )

        pedido = EnvioRPS(
            aliquota_servicos=0.05,
            codigo_servico=7617,
            data_emissao=date(2015, 1, 20),
            discriminacao="Desenvolvimento de Web Site Pessoal.",
            email_tomador="tomador@teste.com.br",
            endereco_bairro="Bela Vista",
            endereco_cep="1310100",
            endereco_cidade=3550308,
            endereco_complemento="Cj 35",
            endereco_logradouro="Paulista",
            endereco_numero="100",
            endereco_tipo_logradouro="Av",
            endereco_uf="SP",
            inscricao_prestador="39616924",
            iss_retido=False,
            numero_rps=4105,
            razao_social_tomador="TOMADOR PF",
            remetente="99999997000100",
            serie_rps="BB",
            status_rps="N",
            tipo_rps="RPS-M",
            tomador="12345678909",
            tributacao_rps="T",
            valor_cofins_centavos=1000,
            valor_csll_centavos=1000,
            valor_deducoes_centavos=500000,
            valor_inss_centavos=1000,
            valor_ir_centavos=1000,
            valor_pis_centavos=1000,
            valor_servicos_centavos=2050000,
        )
        pedido_xml = assinador.assinar_xml(pedido.gerar_xml(assinador=assinador))
        assert_xml_iguais(
            pedido_xml, exemplo_xml, ignorar_tags=["Assinatura", "Signature"]
        )
        schema = XMLSchema(
            file=Path(__file__).parent / "xsds" / "PedidoEnvioRPS_v01.xsd"
        )
        schema.assertValid(pedido_xml)
