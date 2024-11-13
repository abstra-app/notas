from unittest import TestCase
from .envio_rps import RPS, EnvioLoteRPS, RetornoEnvioRpsLote, ChaveNFeRPS
from pathlib import Path
from lxml.etree import fromstring
from datetime import date
from .cliente import ClienteMock
from abstra_notas.assinatura import AssinadorMock
from abstra_notas.validacoes.xml_iguais import assert_xml_iguais

input_exemplo = dict(
    remetente="99999998000228",
    transacao=False,
    data_inicio_periodo_transmitido="2015-01-01",
    data_fim_periodo_transmitido=date(2015, 1, 26),
    lista_rps=[
        RPS(
            inscricao_prestador="39617106",
            serie_rps="BB",
            numero_rps=4102,
            tipo_rps="RPS",
            data_emissao=date(2015, 1, 20),
            status_rps="N",
            tributacao_rps="T",
            valor_servicos_centavos=100_00,
            valor_deducoes_centavos=0,
            valor_pis_centavos=1_01,
            valor_cofins_centavos=1_02,
            valor_inss_centavos=1_03,
            valor_ir_centavos=1_04,
            valor_csll_centavos=1_05,
            codigo_servico=7811,
            aliquota_servicos=0.05,
            iss_retido=False,
            tomador="99999999727",
            razao_social_tomador="ANTONIO PRUDENTE",
            endereco_tipo_logradouro="RUA",
            endereco_logradouro="PEDRO AMERICO",
            endereco_numero=1,
            endereco_complemento="1 ANDAR",
            endereco_bairro="CENTRO",
            endereco_cidade=3550308,
            endereco_uf="SP",
            endereco_cep="00001045",
            email_tomador="teste@teste.com",
            discriminacao="Nota Fiscal de Teste Emitida por Cliente Web",
            valor_carga_tributaria_centavos=30_25,
            percentual_carga_tributaria=0.1512,
            fonte_carga_tributaria="IBPT",
        ),
        dict(
            inscricao_prestador="39617106",
            serie_rps="BC",
            numero_rps=4103,
            tipo_rps="RPS",
            data_emissao="2015-01-21",
            status_rps="N",
            tributacao_rps="F",
            valor_servicos_centavos=101_00,
            valor_deducoes_centavos=0,
            valor_pis_centavos=2_01,
            valor_cofins_centavos=2_02,
            valor_inss_centavos=2_03,
            valor_ir_centavos=2_04,
            valor_csll_centavos=2_05,
            codigo_servico=7811,
            aliquota_servicos=0.05,
            iss_retido=False,
            tomador="99999999727",
            razao_social_tomador="ANTONIO PRUDENTE",
            endereco_tipo_logradouro="RUA",
            endereco_logradouro="PEDRO AMERICO",
            endereco_numero=1,
            endereco_complemento="1 ANDAR",
            endereco_bairro="CENTRO",
            endereco_cidade=3550308,
            endereco_uf="SP",
            endereco_cep="00001045",
            email_tomador="teste@teste.com",
            discriminacao="Nota Fiscal 2 de Teste Emitida por Cliente Web",
            valor_carga_tributaria_centavos=20_21,
            percentual_carga_tributaria=0.1714,
            fonte_carga_tributaria="IBPT",
            municipio_prestacao=1200013,
        ),
    ],
)


class EnvioLoteTest(TestCase):
    def test_exemplo(self):
        assinador = AssinadorMock()
        self.maxDiff = None
        exemplo_path = Path(__file__).parent / "exemplos" / "PedidoEnvioLoteRPS.xml"
        exemplo_xml = assinador.assinar_xml(
            fromstring(exemplo_path.read_text(encoding="utf-8"))
        )

        pedido = EnvioLoteRPS(
            **input_exemplo,
        )
        pedido_xml = assinador.assinar_xml(pedido.gerar_xml(assinador=assinador))
        assert_xml_iguais(
            pedido_xml, exemplo_xml, ignorar_tags=["Assinatura", "Signature"]
        )

        cliente = ClienteMock()

        resultado = cliente.gerar_notas_em_lote(pedido)
        self.assertEqual(
            resultado,
            RetornoEnvioRpsLote(
                numero_lote=42686544,
                inscricao_prestador=39617106,
                remetente="99999998000228",
                data_envio_lote=date(2015, 1, 26),
                qtd_notas_processadas=2,
                tempo_processamento=1,
                valor_total_servicos=201,
                chaves_nfe_rps=[
                    ChaveNFeRPS(
                        chave_nfe_codigo_verificacao="2QFFXUMK",
                        chave_nfe_inscricao_prestador=39617106,
                        chave_nfe_numero_nfe=3,
                        chave_rps_inscricao_prestador=39617106,
                        chave_rps_numero_rps=4102,
                        chave_rps_serie_rps="BB",
                    ),
                    ChaveNFeRPS(
                        chave_nfe_codigo_verificacao="G9TBE9PR",
                        chave_nfe_inscricao_prestador=39617106,
                        chave_nfe_numero_nfe=4,
                        chave_rps_inscricao_prestador=39617106,
                        chave_rps_numero_rps=4103,
                        chave_rps_serie_rps="BC",
                    ),
                ],
            ),
        )
