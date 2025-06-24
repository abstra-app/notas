from dataclasses import dataclass
from typing import Literal, List, Optional
from lxml.etree import Element, fromstring, ElementBase
import base64
from dateutil.parser import parse
from abstra_notas.validacoes.email import validar_email
from abstra_notas.validacoes.cidades import validar_codigo_cidade, normalizar_uf, UF
from abstra_notas.validacoes.cpfcnpj import normalizar_cpf_ou_cnpj, cpf_ou_cnpj
from abstra_notas.validacoes.cep import normalizar_cep
from abstra_notas.validacoes.tipo_logradouro import TipoLogradouro
from datetime import date
from .remessa import Remessa
from .pedido import Pedido
from .retorno import Retorno
from .templates import load_template
from abstra_notas.assinatura import Assinador
from .erro import Erro


@dataclass
class ChaveNFeRPS(Retorno):
    chave_nfe_inscricao_prestador: str
    chave_nfe_numero_nfe: int
    chave_nfe_codigo_verificacao: str
    chave_rps_inscricao_prestador: str
    chave_rps_serie_rps: str
    chave_rps_numero_rps: int

    def __post_init__(self):
        if isinstance(self.chave_nfe_inscricao_prestador, int):
            self.chave_nfe_inscricao_prestador = str(self.chave_nfe_inscricao_prestador)

        if isinstance(self.chave_rps_inscricao_prestador, int):
            self.chave_rps_inscricao_prestador = str(self.chave_rps_inscricao_prestador)

    @staticmethod
    def ler_xml(xml: ElementBase) -> "ChaveNFeRPS":
        return ChaveNFeRPS(
            chave_nfe_inscricao_prestador=xml.find(".//ChaveNFe")
            .find(".//InscricaoPrestador")
            .text,
            chave_nfe_codigo_verificacao=xml.find(".//ChaveNFe")
            .find(".//CodigoVerificacao")
            .text,
            chave_nfe_numero_nfe=int(xml.find(".//ChaveNFe").find(".//NumeroNFe").text),
            chave_rps_inscricao_prestador=xml.find(".//ChaveRPS")
            .find(".//InscricaoPrestador")
            .text,
            chave_rps_numero_rps=int(xml.find(".//ChaveRPS").find(".//NumeroRPS").text),
            chave_rps_serie_rps=xml.find(".//ChaveRPS").find(".//SerieRPS").text,
        )


@dataclass
class RetornoEnvioRps(ChaveNFeRPS):
    @staticmethod
    def ler_xml(xml: ElementBase) -> "RetornoEnvioRps":
        sucesso = xml.find(".//Sucesso").text
        if sucesso == "false":
            raise ErroEnvioRps(
                codigo=xml.find(".//Codigo").text,
                descricao=xml.find(".//Descricao").text,
            )
        elif sucesso == "true":
            chave = ChaveNFeRPS.ler_xml(xml)
            return RetornoEnvioRps(**chave.__dict__)


@dataclass
class ErroEnvioRps(Erro):
    codigo: int
    descricao: str


@dataclass
class RPS:
    inscricao_prestador: int
    numero_rps: int
    tipo_rps: Literal["RPS", "RPS-M", "RPS-C"]
    data_emissao: date
    discriminacao: str
    status_rps: Literal["N", "C"]
    tributacao_rps: Literal["T", "F", "A", "B", "D", "M", "N", "R", "S", "X", "V", "P"]
    codigo_servico: str
    aliquota_servicos: float
    iss_retido: bool
    valor_servicos_centavos: int
    valor_deducoes_centavos: int
    serie_rps: str

    valor_pis_centavos: Optional[int] = None
    valor_cofins_centavos: Optional[int] = None
    valor_inss_centavos: Optional[int] = None
    valor_ir_centavos: Optional[int] = None
    valor_csll_centavos: Optional[int] = None
    valor_carga_tributaria_centavos: Optional[int] = None
    valor_total_recebido_centavos: Optional[int] = None

    tomador: Optional[str] = None
    inscricao_municipal_tomador: Optional[str] = None
    inscricao_estadual_tomador: Optional[str] = None
    razao_social_tomador: Optional[str] = None
    email_tomador: Optional[str] = None

    endereco_tipo_logradouro: Optional[TipoLogradouro] = None
    endereco_logradouro: Optional[str] = None
    endereco_numero: Optional[str] = None
    endereco_complemento: Optional[str] = None
    endereco_uf: Optional[UF] = None
    endereco_cidade: Optional[int] = None
    endereco_bairro: Optional[str] = None
    endereco_cep: Optional[str] = None

    intermediario: Optional[str] = None
    inscricao_municipal_intermediario: Optional[str] = None
    iss_retido_intermediario: Optional[bool] = None
    email_intermediario: Optional[str] = None

    percentual_carga_tributaria: Optional[float] = None
    fonte_carga_tributaria: Optional[str] = None
    codigo_cei: Optional[int] = None
    matricula_obra: Optional[int] = None
    municipio_prestacao: Optional[int] = None
    numero_encapsulamento: Optional[int] = None

    def __post_init__(self):
        if isinstance(self.data_emissao, str):
            self.data_emissao = parse(self.data_emissao).date()

        if self.endereco_cep is not None:
            self.endereco_cep = normalizar_cep(self.endereco_cep)

        if self.endereco_uf is not None:
            if isinstance(self.endereco_uf, str):
                uf_str = self.endereco_uf
            else:
                uf_str = self.endereco_uf.value
            self.endereco_uf = UF(normalizar_uf(uf_str))

        if self.tomador is not None:
            self.tomador = normalizar_cpf_ou_cnpj(self.tomador)

        if self.endereco_cidade is not None:
            assert validar_codigo_cidade(
                self.endereco_cidade
            ), f"Código de cidade inválido: {self.endereco_cidade}"

        if isinstance(self.endereco_tipo_logradouro, str):
            if self.endereco_tipo_logradouro.upper() in TipoLogradouro.__members__:
                self.endereco_tipo_logradouro = TipoLogradouro[
                    self.endereco_tipo_logradouro.upper()
                ]
            else:
                self.endereco_tipo_logradouro = TipoLogradouro(
                    self.endereco_tipo_logradouro.upper()
                )

        assert (
            self.aliquota_servicos >= 0 and self.aliquota_servicos <= 1
        ), "A alíquota de serviços deve ser um valor entre 0 e 1"

        if isinstance(self.codigo_servico, int):
            self.codigo_servico = str(self.codigo_servico).zfill(4)
        elif isinstance(self.codigo_servico, str):
            assert len(self.codigo_servico) in [
                4,
                5,
            ], "Código de serviço deve ter 4 ou 5 dígitos"

        assert self.email_tomador is None or validar_email(
            self.email_tomador
        ), f"Email do tomador com formato inválido: {self.email_tomador}"

        assert (
            isinstance(self.valor_servicos_centavos, int)
            and self.valor_servicos_centavos >= 0
        ), "O valor de serviços deve ser um valor decimal maior ou igual a zero"

        if self.serie_rps is not None:
            self.serie_rps = self.serie_rps.strip()
            assert (
                len(self.serie_rps) <= 5
            ), "A série do RPS deve ter no máximo 5 caracteres"

    def gerar_string_xml(self, assinador: Assinador) -> str:
        template = load_template("RPS")
        return template.render(
            inscricao_prestador=str(self.inscricao_prestador).zfill(8),
            serie_rps=self.serie_rps,
            numero_rps=self.numero_rps,
            tipo_rps=self.tipo_rps,
            data_emissao=self.data_emissao,
            status_rps=self.status_rps,
            tributacao_rps=self.tributacao_rps,
            valor_servicos=f"{self.valor_servicos_centavos / 100:.2f}",
            valor_deducoes=f"{self.valor_deducoes_centavos / 100:.2f}"
            if self.valor_deducoes_centavos is not None
            else None,
            codigo_servico=self.codigo_servico,
            aliquota_servicos=self.aliquota_servicos,
            iss_retido=str(self.iss_retido).lower(),
            tomador=self.tomador,
            tomador_tipo=self.tomador_tipo,
            razao_social_tomador=self.razao_social_tomador,
            discriminacao=self.discriminacao,
            assinatura=self.assinatura(assinador),
        )

    def assinatura(self, assinador: Assinador) -> str:
        template = ""
        template += str(self.inscricao_prestador).zfill(8)
        template += self.serie_rps.upper() + (5 - len(self.serie_rps)) * " "
        template += str(self.numero_rps).zfill(12)
        template += self.data_emissao.strftime("%Y%m%d").upper()
        template += self.tributacao_rps
        template += self.status_rps
        template += self.iss_retido == "true" and "S" or "N"
        template += str(self.valor_servicos_centavos).zfill(15)
        template += str(self.valor_deducoes_centavos).zfill(15)
        template += self.codigo_servico.zfill(5)

        template_bytes = template.encode("ascii")
        signed_template = assinador.assinar_bytes_rsa_sh1(template_bytes)
        return base64.b64encode(signed_template).decode("ascii")

    @property
    def tomador_tipo(self) -> Optional[Literal["CPF", "CNPJ"]]:
        return cpf_ou_cnpj(self.tomador) if self.tomador is not None else None

    @property
    def intermediario_tipo(self) -> Optional[Literal["CPF", "CNPJ"]]:
        return (
            cpf_ou_cnpj(self.intermediario) if self.intermediario is not None else None
        )


@dataclass
class EnvioRPS(RPS, Pedido, Remessa):
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


@dataclass
class RetornoEnvioRpsLote(Retorno):
    numero_lote: int
    inscricao_prestador: int
    remetente: str
    data_envio_lote: date
    qtd_notas_processadas: int
    tempo_processamento: int
    valor_total_servicos: int
    chaves_nfe_rps: List[ChaveNFeRPS]

    @staticmethod
    def ler_xml(xml: Element) -> "RetornoEnvioRpsLote":
        if xml.find(".//Sucesso").text == "false":
            raise ErroEnvioRps(
                codigo=xml.find(".//Codigo").text,
                descricao=xml.find(".//Descricao").text,
            )
        return RetornoEnvioRpsLote(
            numero_lote=int(xml.find(".//NumeroLote").text),
            inscricao_prestador=int(xml.find(".//InscricaoPrestador").text),
            remetente=xml.find(".//CPFCNPJRemetente").find(".//CNPJ").text,
            data_envio_lote=parse(xml.find(".//DataEnvioLote").text).date(),
            qtd_notas_processadas=int(xml.find(".//QtdNotasProcessadas").text),
            tempo_processamento=int(xml.find(".//TempoProcessamento").text),
            valor_total_servicos=int(xml.find(".//ValorTotalServicos").text),
            chaves_nfe_rps=[
                ChaveNFeRPS.ler_xml(retorno)
                for retorno in xml.findall(".//ChaveNFeRPS")
            ],
        )


@dataclass
class EnvioLoteRPS(Pedido, Remessa):
    transacao: bool
    data_inicio_periodo_transmitido: date
    data_fim_periodo_transmitido: date
    lista_rps: List[RPS]

    teste: bool = False

    def __post_init__(self):
        if isinstance(self.data_fim_periodo_transmitido, str):
            self.data_fim_periodo_transmitido = parse(
                self.data_fim_periodo_transmitido
            ).date()

        if isinstance(self.data_inicio_periodo_transmitido, str):
            self.data_inicio_periodo_transmitido = parse(
                self.data_inicio_periodo_transmitido
            ).date()

        for idx, rps in enumerate(self.lista_rps):
            if isinstance(rps, dict):
                self.lista_rps[idx] = RPS(**rps)

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
            valor_total_deducoes=f"{self.valor_total_deducoes:.2f}",
            lista_rps=[rps.gerar_string_xml(assinador) for rps in self.lista_rps],
        )

        return fromstring(xml)

    @property
    def quantidade_rps(self):
        return len(self.lista_rps)

    @property
    def valor_total_servicos(self):
        return sum(rps.valor_servicos_centavos for rps in self.lista_rps) / 100

    @property
    def valor_total_deducoes(self):
        return sum(rps.valor_deducoes_centavos for rps in self.lista_rps) / 100

    @property
    def remetente_tipo(self) -> Literal["CPF", "CNPJ"]:
        return cpf_ou_cnpj(self.remetente)

    @property
    def metodo(self) -> str:
        if self.teste:
            return "TesteEnvioLoteRPS"
        else:
            return "EnvioLoteRPS"
