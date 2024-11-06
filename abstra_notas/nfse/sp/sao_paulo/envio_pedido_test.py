from unittest import TestCase
from .envio_pedido import (
    PedidoEnvioRPS,
    Cabecalho,
    ChaveRPS,
    RPS,
    CPFCNPJTomador,
    EnderecoTomador,
    StatusRPS,
    TipoRPS,
    TributacaoRPS,
)
from .tipos_comuns import CPFCNPJRemetente
from pathlib import Path
from xml.etree.ElementTree import parse
from datetime import date


class EnvioTest(TestCase):
    def test_exemplo(self):
        self.maxDiff = None
        exemplo_path = Path(__file__).parent / "exemplos" / "PedidoEnvioRPS.xml"
        exemplo_xml = parse(exemplo_path)
        exemplo = PedidoEnvioRPS.parse_xml(exemplo_xml.getroot())

        pedido = PedidoEnvioRPS(
            cabecalho=Cabecalho(CPFCNPJRemetente(tipo="CNPJ", numero="99999997000100")),
            rps=RPS(
                assinatura="d8Pg/jdA7t5tSaB8Il1d/CMiLGgfFAXzTL9o5stv6TNbhm9I94DIo0/ocqJpGx0KzoEeIQz4RSn99pWX4fiW/aETlNT3u5woqCAyL6U2hSyl/eQfWRYrqFu2zcdc4rsAG/wJbDjNO8y0Pz9b6rlTwkIJ+kMdLo+EWXMnB744olYE721g2O9CmUTvjtBgCfVUgvuN1MGjgzpgyussCOSkLpGbrqtM5+pYMXZsTaEVIIck1baDkoRpLmZ5Y/mcn1/Om1fMyhJVUAkgI5xBrORuotIP7e3+HLJnKgzQQPWCtLyEEyAqUk9Gq64wMayITua5FodaJsX+Eic/ie3kS5m50Q==",
                chave_rps=ChaveRPS(
                    inscricao_prestador="39616924", serie_rps="BB", numero_rps=4105
                ),
                aliquota_servicos=0.05,
                codigo_servico=7617,
                cpf_cnpj_tomador=CPFCNPJTomador(tipo="CPF", numero="12345678909"),
                data_emissao=date(2015, 1, 20),
                discriminacao="Desenvolvimento de Web Site Pessoal.",
                email_tomador="tomador@teste.com.br",
                endereco_tomador=EnderecoTomador(
                    bairro="Bela Vista",
                    cep="1310100",
                    cidade=3550308,
                    complemento_endereco="Cj 35",
                    logradouro="Paulista",
                    numero_endereco="100",
                    tipo_logradouro="Av",
                    uf="SP",
                ),
                iss_retido=False,
                razao_social_tomador="TOMADOR PF",
                status_rps=StatusRPS.NORMAL,
                tipo_rps=TipoRPS.RPS_M,
                tributacao_rps=TributacaoRPS.T,
                valor_cofins=10,
                valor_csll=10,
                valor_deducoes=5000,
                valor_inss=10,
                valor_ir=10,
                valor_pis=10,
                valor_servicos=20500,
            ),
        )

        self.assertEqual(exemplo, pedido)
