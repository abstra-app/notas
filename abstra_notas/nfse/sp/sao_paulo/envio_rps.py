from dataclasses import dataclass
from typing import Literal, Tuple
from lxml.etree import Element, fromstring
import base64
from abstra_notas.validacoes.email import validar_email
from abstra_notas.validacoes.cidades import validar_codigo_cidade, normalizar_uf
from abstra_notas.validacoes.cpf import normalizar_cpf
from abstra_notas.validacoes.cnpj import normalizar_cnpj
from .codigos_de_servico import codigos_de_servico_validos
from datetime import date
from jinja2 import Template
from pathlib import Path
from .pedido import Pedido
from .retorno import Retorno
from abstra_notas.assinatura import Assinador


@dataclass
class RetornoEnvioRPS(Retorno):
    sucesso: bool
    chave_nfe_inscricao_prestador: str
    chave_nfe_numero_nfe: str
    chave_nfe_codigo_verificacao: str
    chave_rps_inscricao_prestador: str
    chave_rps_serie_rps: str
    chave_rps_numero_rps: str

    @staticmethod
    def ler_xml(xml: Element) -> "RetornoEnvioRPS":
        return RetornoEnvioRPS(
            sucesso=xml.find(".//Sucesso").text == "true",
            chave_nfe_inscricao_prestador=xml.find(".//InscricaoPrestador").text,
            chave_nfe_codigo_verificacao=xml.find(".//CodigoVerificacao").text,
            chave_nfe_numero_nfe=xml.find(".//NumeroNFe").text,
            chave_rps_inscricao_prestador=xml.find(".//InscricaoPrestador").text,
            chave_rps_numero_rps=xml.find(".//NumeroRPS").text,
            chave_rps_serie_rps=xml.find(".//SerieRPS").text,
        )


@dataclass
class PedidoEnvioRPS(Pedido):
    remetente: Tuple[Literal["CPF", "CNPJ"], str]
    inscricao_prestador: str
    serie_rps: str
    numero_rps: int
    tipo_rps: Literal["RPS", "RPS-M", "RPS-C"]
    data_emissao: date
    status_rps: Literal["N", "C"]
    tributacao_rps: Literal["T", "F", "A", "B", "D", "M", "N", "R", "S", "X", "V", "P"]
    valor_servicos_centavos: int
    valor_deducoes_centavos: int
    valor_pis_centavos: int
    valor_cofins_centavos: int
    valor_inss_centavos: int
    valor_ir_centavos: int
    valor_csll_centavos: int
    codigo_servico: int
    aliquota_servicos: float
    iss_retido: Literal["true", "false"]
    tomador: Tuple[Literal["CPF", "CNPJ"], str]
    razao_social_tomador: str
    endereco_tipo_logradouro: str
    endereco_logradouro: str
    endereco_numero: str
    endereco_complemento: str
    endereco_bairro: str
    endereco_cidade: int
    endereco_uf: str
    endereco_cep: str
    email_tomador: str
    discriminacao: str

    def __post_init__(self):
        if self.tomador[0] == "CPF":
            self.tomador = ("CPF", normalizar_cpf(self.tomador[1]))
        if self.tomador[0] == "CNPJ":
            self.tomador = ("CNPJ", normalizar_cnpj(self.tomador[1]))
        self.endereco_uf = normalizar_uf(self.endereco_uf)
        assert validar_codigo_cidade(
            self.endereco_cidade
        ), f"Código de cidade inválido: {self.endereco_cidade}"
        assert (
            self.aliquota_servicos >= 0 and self.aliquota_servicos <= 1
        ), "A alíquota de serviços deve ser um valor entre 0 e 1"
        assert (
            self.codigo_servico in codigos_de_servico_validos
        ), f"Código de serviço inválido, os códigos válidos são: {codigos_de_servico_validos}"
        assert validar_email(
            self.email_tomador
        ), f"Email do tomador com formato inválido: {self.email_tomador}"
        assert isinstance(
            self.valor_servicos_centavos, int
        ), "O valor de serviços deve ser um valor decimal"
        assert isinstance(
            self.valor_deducoes_centavos, int
        ), "O valor de deduções deve ser um valor decimal"
        assert isinstance(
            self.valor_pis_centavos, int
        ), "O valor de PIS deve ser um valor decimal"
        assert isinstance(
            self.valor_cofins_centavos, int
        ), "O valor de COFINS deve ser um valor decimal"
        assert isinstance(
            self.valor_inss_centavos, int
        ), "O valor de INSS deve ser um valor decimal"
        assert isinstance(
            self.valor_ir_centavos, int
        ), "O valor de IR deve ser um valor decimal"
        assert isinstance(
            self.valor_csll_centavos, int
        ), "O valor de CSLL deve ser um valor decimal"
        assert (
            self.valor_servicos_centavos >= 0
        ), "O valor de serviços deve ser maior ou igual a zero"
        assert (
            self.valor_deducoes_centavos >= 0
        ), "O valor de deduções deve ser maior ou igual a zero"
        assert (
            self.valor_pis_centavos >= 0
        ), "O valor de PIS deve ser maior ou igual a zero"
        assert (
            self.valor_cofins_centavos >= 0
        ), "O valor de COFINS deve ser maior ou igual a zero"
        assert (
            self.valor_inss_centavos >= 0
        ), "O valor de INSS deve ser maior ou igual a zero"
        assert (
            self.valor_ir_centavos >= 0
        ), "O valor de IR deve ser maior ou igual a zero"
        assert (
            self.valor_csll_centavos >= 0
        ), "O valor de CSLL deve ser maior ou igual a zero"
        assert (
            self.valor_servicos_centavos
            - self.valor_deducoes_centavos
            - self.valor_pis_centavos
            - self.valor_cofins_centavos
            - self.valor_inss_centavos
            - self.valor_ir_centavos
            - self.valor_csll_centavos
            >= 0
        ), "A soma dos valores não pode ser negativa"

    def gerar_xml(self, assinador: Assinador) -> Element:
        xml = self.template.render(
            **self.__dict__, assinatura=self.assinatura(assinador)
        )

        return fromstring(xml)

    @property
    def nome_metodo(self):
        return "EnvioRPS"

    def assinatura(self, assinador: Assinador) -> str:
        template = ""
        template += str(self.inscricao_prestador)
        template += self.serie_rps.upper()
        template += str(self.numero_rps).zfill(12)
        template += self.data_emissao.strftime("%Y%m%d").upper()
        template += self.tributacao_rps
        template += self.status_rps
        template += self.iss_retido == "true" and "S" or "N"
        template += str(self.valor_servicos_centavos).zfill(15)
        template += str(self.valor_deducoes_centavos).zfill(15)
        template += str(self.codigo_servico).zfill(5)
        if self.tomador[0] == "CPF":
            template += "1"
        elif self.tomador[0] == "CNPJ":
            template += "2"
        else:
            template += "3"
        template += (
            self.tomador[1].replace(".", "").replace("-", "").replace("/", "").zfill(14)
        )

        template_bytes = template.encode("ascii")

        signed_template = assinador.assinar_bytes_rsa_sh1(template_bytes)
        return base64.b64encode(signed_template).decode("ascii")

    @property
    def classe_retorno(self):
        return RetornoEnvioRPS
