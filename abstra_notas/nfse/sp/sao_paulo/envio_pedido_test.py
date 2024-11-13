from unittest import TestCase
from .envio_rps import EnvioRPS, RetornoEnvioRps
from pathlib import Path
from lxml.etree import fromstring
from datetime import date
from .cliente import ClienteMock
from abstra_notas.assinatura import AssinadorMock
from abstra_notas.validacoes.xml_iguais import assert_xml_iguais

parametros_opcionais = [
    f
    for f in EnvioRPS.__dataclass_fields__.keys()
    if not EnvioRPS.__dataclass_fields__[f].default
]

input_exemplo = dict(
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


class EnvioTest(TestCase):
    def test_exemplo(self):
        assinador = AssinadorMock()
        self.maxDiff = None
        exemplo_path = Path(__file__).parent / "exemplos" / "PedidoEnvioRPS.xml"
        exemplo_xml = assinador.assinar_xml(
            fromstring(exemplo_path.read_text(encoding="utf-8"))
        )

        pedido = EnvioRPS(
            **input_exemplo,
        )
        pedido_xml = assinador.assinar_xml(pedido.gerar_xml(assinador=assinador))
        assert_xml_iguais(
            pedido_xml, exemplo_xml, ignorar_tags=["Assinatura", "Signature"]
        )

        cliente = ClienteMock()

        resultado = cliente.gerar_nota(pedido)
        self.assertEqual(
            resultado,
            RetornoEnvioRps(
                chave_nfe_codigo_verificacao="PH5GL6XU",
                chave_nfe_inscricao_prestador="39616924",
                chave_nfe_numero_nfe=17943,
                chave_rps_inscricao_prestador="39616924",
                chave_rps_numero_rps=4105,
                chave_rps_serie_rps="BB",
            ),
        )

    def test_minimo(self):
        assinador = AssinadorMock()
        self.maxDiff = None
        exemplo_path = Path(__file__).parent / "exemplos" / "PedidoEnvioRPS.xml"
        assinador.assinar_xml(fromstring(exemplo_path.read_text(encoding="utf-8")))

        pedido = EnvioRPS(
            **{k: v for k, v in input_exemplo.items() if k not in parametros_opcionais},
        )
        assinador.assinar_xml(pedido.gerar_xml(assinador=assinador))

        cliente = ClienteMock()

        resultado = cliente.gerar_nota(pedido)
        self.assertEqual(
            resultado,
            RetornoEnvioRps(
                chave_nfe_codigo_verificacao="PH5GL6XU",
                chave_nfe_inscricao_prestador="39616924",
                chave_nfe_numero_nfe=17943,
                chave_rps_inscricao_prestador="39616924",
                chave_rps_numero_rps=4105,
                chave_rps_serie_rps="BB",
            ),
        )

    def test_maximo(self):
        assinador = AssinadorMock()
        self.maxDiff = None
        exemplo_path = Path(__file__).parent / "exemplos" / "PedidoEnvioRPS.xml"
        assinador.assinar_xml(fromstring(exemplo_path.read_text(encoding="utf-8")))
        input_maximo = dict(
            **input_exemplo,
            valor_carga_tributaria_centavos=100,
            valor_total_recebido_centavos=101,
            inscricao_municipal_tomador="12345678",
            inscricao_estadual_tomador="123456",
            intermediario="12345678909",
            inscricao_municipal_intermediario="12345678",
            iss_retido_intermediario=True,
            email_intermediario="intermediario@email.com",
            percentual_carga_tributaria=0.05,
            fonte_carga_tributaria="Fonte",
            codigo_cei="123456",
            matricula_obra="123456",
            municipio_prestacao=3550308,
            numero_encapsulamento=123456,
        )

        parametros_faltantes = [
            p for p in parametros_opcionais if p not in input_maximo
        ]
        if len(parametros_faltantes) > 0:
            raise ValueError(
                f"Os seguintes parâmetros opcionais não foram incluídos: {parametros_faltantes}"
            )

        pedido = EnvioRPS(
            **input_maximo,
        )
        assinador.assinar_xml(pedido.gerar_xml(assinador=assinador))

        cliente = ClienteMock()

        resultado = cliente.gerar_nota(pedido)
        self.assertEqual(
            resultado,
            RetornoEnvioRps(
                chave_nfe_codigo_verificacao="PH5GL6XU",
                chave_nfe_inscricao_prestador="39616924",
                chave_nfe_numero_nfe=17943,
                chave_rps_inscricao_prestador="39616924",
                chave_rps_numero_rps=4105,
                chave_rps_serie_rps="BB",
            ),
        )
