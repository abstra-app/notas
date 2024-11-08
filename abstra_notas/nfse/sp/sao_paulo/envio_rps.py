from dataclasses import dataclass
from typing import Literal, Union, List
from lxml.etree import Element, fromstring, tostring
import base64
from abstra_notas.validacoes.email import validar_email
from abstra_notas.validacoes.cidades import validar_codigo_cidade, normalizar_uf
from abstra_notas.validacoes.cpfcnpj import normalizar_cpf_ou_cnpj, cpf_ou_cnpj
from .codigos_de_servico import codigos_de_servico_validos
from datetime import date
from .pedido import Pedido
from .retorno import Retorno
from .templates import load_template
from abstra_notas.assinatura import Assinador
from .cliente import Cliente


class RetornoEnvioRPS(Retorno):
    @dataclass
    class RetornoEnvioRpsSucesso:
        chave_nfe_inscricao_prestador: str
        chave_nfe_numero_nfe: str
        chave_nfe_codigo_verificacao: str
        chave_rps_inscricao_prestador: str
        chave_rps_serie_rps: str
        chave_rps_numero_rps: str

        @property
        def sucesso(self):
            return True

        @staticmethod
        def ler_xml(xml: str):
            xml = fromstring(xml.encode("utf-8"))
            return RetornoEnvioRPS.RetornoEnvioRpsSucesso(
                chave_nfe_inscricao_prestador=xml.find(".//InscricaoPrestador").text,
                chave_nfe_codigo_verificacao=xml.find(".//CodigoVerificacao").text,
                chave_nfe_numero_nfe=xml.find(".//NumeroNFe").text,
                chave_rps_inscricao_prestador=xml.find(".//InscricaoPrestador").text,
                chave_rps_numero_rps=xml.find(".//NumeroRPS").text,
                chave_rps_serie_rps=xml.find(".//SerieRPS").text,
            )

    @dataclass
    class RetornoEnvioRpsErro:
        codigo: int
        descricao: str

        @property
        def sucesso(self):
            return False

        @staticmethod
        def ler_xml(xml: Element):
            return RetornoEnvioRPS.RetornoEnvioRpsErro(
                codigo=int(xml.find(".//Codigo").text),
                descricao=xml.find(".//Descricao").text,
            )

    @staticmethod
    def ler_xml(xml):
        xml = xml.encode("utf-8")
        xml = fromstring(xml)
        sucesso = xml.find(".//Sucesso").text == "true"
        if sucesso:
            return RetornoEnvioRPS.RetornoEnvioRpsSucesso.ler_xml(xml)
        else:
            return RetornoEnvioRPS.RetornoEnvioRpsErro.ler_xml(xml)


@dataclass
class RPS:
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
    iss_retido: bool
    tomador: str
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
        self.tomador = normalizar_cpf_ou_cnpj(self.tomador)
        self.endereco_uf = normalizar_uf(self.endereco_uf)
        assert validar_codigo_cidade(
            self.endereco_cidade
        ), f"Código de cidade inválido: {self.endereco_cidade}"
        assert (
            self.aliquota_servicos >= 0 and self.aliquota_servicos <= 1
        ), "A alíquota de serviços deve ser um valor entre 0 e 1"
        # assert (
        #     self.codigo_servico in codigos_de_servico_validos
        # ), f"Código de serviço inválido, os códigos válidos são: {codigos_de_servico_validos}"
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

    def gerar_string_xml(self, assinador: Assinador) -> Element:
        template = load_template("RPS")
        return template.render(
            inscricao_prestador=self.inscricao_prestador,
            serie_rps=self.serie_rps,
            numero_rps=self.numero_rps,
            tipo_rps=self.tipo_rps,
            data_emissao=self.data_emissao,
            status_rps=self.status_rps,
            tributacao_rps=self.tributacao_rps,
            valor_servicos=f"{self.valor_servicos_centavos / 100:.2f}",
            valor_deducoes=f"{self.valor_deducoes_centavos / 100:.2f}",
            valor_pis=f"{self.valor_pis_centavos / 100:.2f}",
            valor_cofins=f"{self.valor_cofins_centavos / 100:.2f}",
            valor_inss=f"{self.valor_inss_centavos / 100:.2f}",
            valor_ir=f"{self.valor_ir_centavos / 100:.2f}",
            valor_csll=f"{self.valor_csll_centavos / 100:.2f}",
            codigo_servico=self.codigo_servico,
            aliquota_servicos=self.aliquota_servicos,
            iss_retido=str(self.iss_retido).lower(),
            tomador=self.tomador,
            tomador_tipo=self.tomador_tipo,
            razao_social_tomador=self.razao_social_tomador,
            endereco_tipo_logradouro=self.endereco_tipo_logradouro,
            endereco_logradouro=self.endereco_logradouro,
            endereco_numero=self.endereco_numero,
            endereco_complemento=self.endereco_complemento,
            endereco_bairro=self.endereco_bairro,
            endereco_cidade=self.endereco_cidade,
            endereco_uf=self.endereco_uf,
            endereco_cep=self.endereco_cep,
            email_tomador=self.email_tomador,
            discriminacao=self.discriminacao,
            assinatura=self.assinatura(assinador),
        )

    def assinatura(self, assinador: Assinador) -> str:
        template = ""
        template += self.inscricao_prestador
        template += self.serie_rps.upper()
        template += str(self.numero_rps).zfill(12)
        template += self.data_emissao.strftime("%Y%m%d").upper()
        template += self.tributacao_rps
        template += self.status_rps
        template += self.iss_retido == "true" and "S" or "N"
        template += str(self.valor_servicos_centavos).zfill(15)
        template += str(self.valor_deducoes_centavos).zfill(15)
        template += str(self.codigo_servico).zfill(5)
        if self.tomador_tipo == "CPF":
            template += "1"
        elif self.tomador_tipo == "CNPJ":
            template += "2"
        else:
            template += "3"
        template += (
            self.tomador.replace(".", "").replace("-", "").replace("/", "").zfill(14)
        )

        template_bytes = template.encode("ascii")

        signed_template = assinador.assinar_bytes_rsa_sh1(template_bytes)
        return base64.b64encode(signed_template).decode("ascii")

    @property
    def tomador_tipo(self) -> Literal["CPF", "CNPJ"]:
        return cpf_ou_cnpj(self.tomador)


@dataclass
class EnvioRPS(RPS, Pedido):
    remetente: str

    def gerar_xml(self, assinador: Assinador) -> Element:
        xml = self.template.render(
            remetente=self.remetente,
            remetente_tipo=self.remetente_tipo,
            rps=self.gerar_string_xml(assinador),
        )

        return fromstring(xml)

    @property
    def nome_metodo(self):
        return "EnvioRPS"

    @property
    def classe_retorno(self):
        return RetornoEnvioRPS

    @property
    def remetente_tipo(self) -> Literal["CPF", "CNPJ"]:
        return cpf_ou_cnpj(self.remetente)

    def executar(
        self, cliente: Cliente
    ) -> Union[
        RetornoEnvioRPS.RetornoEnvioRpsSucesso, RetornoEnvioRPS.RetornoEnvioRpsErro
    ]:
        return cliente.executar(self)


@dataclass
class EnvioLoteRps(Pedido):
    remetente: str
    transacao: bool
    data_inicio_periodo_transmitido: date
    data_fim_periodo_transmitido: date
    lista_rps: List[RPS]

    def __post_init__(self):
        assert len(self.lista_rps) > 0, "Deve haver pelo menos um RPS no lote"
        assert len(self.lista_rps) <= 50, "O lote não pode ter mais de 50 RPS"

    def gerar_xml(self, assinador: Assinador) -> Element:
        xml = self.template.render(
            remetente=self.remetente,
            remetente_tipo=self.remetente_tipo,
            transacao=str(self.transacao).lower(),
            dt_inicio=str(self.data_inicio_periodo_transmitido),
            dt_fim=str(self.data_fim_periodo_transmitido),
            qtd_rps=self.quantidade_rps,
            valor_total_servicos=f"{self.valor_total_servicos:.2f}",
            valor_total_deducoes=f"{self.valor_total_deducoes: .2f}",
            lista_rps=[rps.gerar_string_xml(assinador) for rps in self.lista_rps],
        )

        return fromstring(xml)

    @property
    def quantidade_rps(self):
        return len(self.lista_rps)

    @property
    def valor_total_servicos(self):
        return sum(rps.valor_servicos_centavos for rps in self.lista_rps)

    @property
    def valor_total_deducoes(self):
        return sum(rps.valor_deducoes_centavos for rps in self.lista_rps)

    @property
    def remetente_tipo(self) -> Literal["CPF", "CNPJ"]:
        return cpf_ou_cnpj(self.remetente)


class TesteEnvioLoteRps(EnvioLoteRps): ...
