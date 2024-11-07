from unittest import TestCase
from .envio_rps import PedidoEnvioRPS
from pathlib import Path
from lxml.etree import parse, XMLSchema, tostring
from datetime import date
import re
from abstra_notas.assinatura import AssinadorMock


class EnvioTest(TestCase):
    def test_exemplo(self):
        self.maxDiff = None
        exemplo_path = Path(__file__).parent / "exemplos" / "PedidoEnvioRPS.xml"
        exemplo_xml = parse(exemplo_path)

        pedido = PedidoEnvioRPS(
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
            iss_retido="false",
            numero_rps=4105,
            razao_social_tomador="TOMADOR PF",
            remetente=("CNPJ", "99999997000100"),
            serie_rps="BB",
            status_rps="N",
            tipo_rps="RPS-M",
            tomador=("CPF", "12345678909"),
            tributacao_rps="T",
            valor_cofins_centavos=10,
            valor_csll_centavos=10,
            valor_deducoes_centavos=5000,
            valor_inss_centavos=10,
            valor_ir_centavos=10,
            valor_pis_centavos=10,
            valor_servicos_centavos=20500,
        )
        pedido_xml = pedido.gerar_xml(assinador=AssinadorMock())
        pedido_str: str = tostring(pedido_xml, encoding=str)
        exemplo_str: str = tostring(exemplo_xml, encoding=str)
        pattern = r"<Assinador>.*</Assinador>"
        pedido_str = re.sub(pattern, "", pedido_str)
        exemplo_str = re.sub(pattern, "", exemplo_str)

        self.assertEqual(pedido_str, exemplo_str)
        schema = XMLSchema(
            file=Path(__file__).parent / "xsds" / "PedidoEnvioRPS_v01.xsd"
        )
        schema.assertValid(pedido_xml)
