from unittest import TestCase
from .consulta import ConsultaNFe, RetornoConsulta, RetornoNFe
from pathlib import Path
from lxml.etree import fromstring
from .cliente import ClienteMock
from abstra_notas.assinatura import AssinadorMock
from abstra_notas.validacoes.xml_iguais import assert_xml_iguais
from datetime import date


class ConsultaTest(TestCase):
    def test_exemplo(self):
        assinador = AssinadorMock()
        self.maxDiff = None
        exemplo_path = Path(__file__).parent / "exemplos" / "PedidoConsultaNFe.xml"
        exemplo_xml = assinador.assinar_xml(fromstring(exemplo_path.read_bytes()))

        pedido = ConsultaNFe(
            remetente="99999997000100",
            chave_nfe_inscricao_prestador="39616924",
            chave_nfe_numero_nfe=17943,
            chave_rps_inscricao_prestador="39616924",
            chave_rps_serie_rps="BB",
            chave_rps_numero_rps=4106,
        )

        pedido_xml = assinador.assinar_xml(pedido.gerar_xml(assinador=assinador))
        assert_xml_iguais(
            pedido_xml, exemplo_xml, ignorar_tags=["Assinatura", "Signature"]
        )

        cliente = ClienteMock()
        resultado = cliente.consultar_nota(pedido)
        self.assertEqual(
            resultado,
            RetornoConsulta(
                lista_nfe=[
                    RetornoNFe(
                        assinatura="d8Pg/jdA7t5tSaB8Il1d/CMiLGgfFAXzTL9o5stv6TNbhm9I94DIo0/ocqJpGx0KzoEeIQz4RSn99pWX4fiW/aETlNT3u5woqCAyL6U2hSyl/eQfWRYrqFu2zcdc4rsAG/wJbDjNO8y0Pz9b6rlTwkIJ+kMdLo+EWXMnB744olYE721g2O9CmUTvjtBgCfVUgvuN1MGjgzpgyussCOSkLpGbrqtM5+pYMXZsTaEVIIck1baDkoRpLmZ5Y/mcn1/Om1fMyhJVUAkgI5xBrORuotIP7e3+HLJnKgzQQPWCtLyEEyAqUk9Gq64wMayITua5FodaJsX+Eic/ie3kS5m50Q==",
                        chave_nfe_inscricao_prestador="39616924",
                        chave_nfe_numero_nfe=17943,
                        chave_nfe_codigo_verificacao="PH5GL6XU",
                        data_emissao_nfe=date(2015, 1, 28),
                        chave_rps_inscricao_prestador="39616924",
                        chave_rps_serie_rps="BB",
                        chave_rps_numero_rps=4105,
                        tipo_rps="RPS-M",
                        data_emissao_rps=date(2015, 1, 20),
                        cpf_cnpj_prestador="99999997000100",
                        razao_social_prestador="JVA LAVANDERIA LTDA",
                        tipo_logradouro_prestador="R",
                        logradouro_prestador="PEDRO AMERICO",
                        numero_endereco_prestador="00032",
                        complemento_endereco_prestador="27 ANDAR",
                        bairro_prestador="CENTRO",
                        cidade_prestador="3550308",
                        uf_prestador="SP",
                        cep_prestador="1045010",
                        status_nfe="N",
                        tributacao_nfe="T",
                        opcao_simples=4,
                        valor_servicos=20500,
                        valor_deducoes=5000,
                        valor_pis=10,
                        valor_cofins=10,
                        valor_inss=10,
                        valor_ir=10,
                        valor_csll=10,
                        codigo_servico=7617,
                        aliquota_servicos=0.0,
                        valor_iss=0,
                        valor_credito=139.5,
                        iss_retido=False,
                        cpf_cnpj_tomador="12345678909",
                        razao_social_tomador="JOAO TESTE",
                        tipo_logradouro_tomador="R",
                        logradouro_tomador="Sao Bento",
                        numero_endereco_tomador="100",
                        bairro_tomador="Centro",
                        cidade_tomador="3550308",
                        uf_tomador="SP",
                        cep_tomador="1010000",
                        email_tomador="teste@teste.com.br",
                        discriminacao="Desenvolvimento de Web Site Pessoal.",
                        fonte_carga_tributaria=None,
                    ),
                    RetornoNFe(
                        assinatura="XwAGUeJfR3AVRctSPTMyuF0wzkd5LSbsOpFEXxVCLdMI4RP7lGEAYwoHFSCfoL6iYH/XMGAXWpua8YUSjPzAXC//TpFnoaNmpN5f9YvpxhW/0y4NiZfYTBiuLlArDLXSG7691vMixk6xRnAXY1eL4GdgrW8GU8VtLjp1tyku5u+gzfkCJDaLi1h2JplbCCvXtNr7smcJl7srYo/MuyLvuawEBCWPr3TtLtRyEu3fsOX8E3TK6ReF5kJ1BF+lO6SIX0GFw+OxQukPVeJt3WXDGZseV8Uh7GNBgxpTRIf1LU4fSoIDXGDzE0UgNJWRKEgcMbDEECBTCYNHl5vFdmePxA==",
                        chave_nfe_inscricao_prestador="39616924",
                        chave_nfe_numero_nfe=17944,
                        chave_nfe_codigo_verificacao="RAJXWXJP",
                        data_emissao_nfe=date(2015, 1, 28),
                        chave_rps_inscricao_prestador="39616924",
                        chave_rps_serie_rps="BB",
                        chave_rps_numero_rps=4106,
                        tipo_rps="RPS-M",
                        data_emissao_rps=date(2015, 1, 20),
                        cpf_cnpj_prestador="99999997000100",
                        razao_social_prestador="JVA LAVANDERIA LTDA",
                        tipo_logradouro_prestador="R",
                        logradouro_prestador="PEDRO AMERICO",
                        numero_endereco_prestador="00032",
                        complemento_endereco_prestador="27 ANDAR",
                        bairro_prestador="CENTRO",
                        cidade_prestador="3550308",
                        uf_prestador="SP",
                        cep_prestador="1045010",
                        status_nfe="N",
                        tributacao_nfe="T",
                        opcao_simples=4,
                        valor_servicos=20501,
                        valor_deducoes=5000,
                        valor_pis=10,
                        valor_cofins=10,
                        valor_inss=10,
                        valor_ir=10,
                        valor_csll=10,
                        codigo_servico=7617,
                        aliquota_servicos=0.0,
                        valor_iss=0,
                        valor_credito=139.5,
                        iss_retido=False,
                        cpf_cnpj_tomador="12345678909",
                        razao_social_tomador="JOAO TESTE",
                        tipo_logradouro_tomador="R",
                        logradouro_tomador="Sao Bento",
                        numero_endereco_tomador="100",
                        bairro_tomador="Centro",
                        cidade_tomador="3550308",
                        uf_tomador="SP",
                        cep_tomador="1010000",
                        email_tomador="teste@teste.com.br",
                        discriminacao="Desenvolvimento de Web Site Pessoal.",
                        fonte_carga_tributaria=None,
                    ),
                ]
            ),
        )
