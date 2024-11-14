from .pedido import Pedido
from .erro import Erro
from .retorno import Retorno
from .remessa import Remessa
from abstra_notas.assinatura import Assinador
from dataclasses import dataclass
from typing import Optional, List
from lxml.etree import ElementBase, fromstring
from datetime import date
from dateutil.parser import parse


def find_text(xml: ElementBase, xpath: str) -> Optional[str]:
    element = xml.find(xpath)
    return element.text if element is not None else None


def optional_int(arg: Optional[str]) -> Optional[int]:
    return int(arg) if arg is not None else None


def optional_float(arg: Optional[str]) -> Optional[float]:
    return float(arg) if arg is not None else None


def optional_bool(arg: Optional[str]) -> Optional[bool]:
    if arg is None:
        return None
    elif arg == "true":
        return True
    elif arg == "false":
        return False


def optional_date(arg: Optional[str]) -> Optional[date]:
    return parse(arg).date() if arg is not None else None


@dataclass
class RetornoNFe:
    assinatura: str
    chave_nfe_inscricao_prestador: str
    chave_nfe_numero_nfe: int
    chave_nfe_codigo_verificacao: str
    data_emissao_nfe: date
    cpf_cnpj_prestador: str
    razao_social_prestador: str
    tipo_logradouro_prestador: str
    logradouro_prestador: str
    numero_endereco_prestador: str
    complemento_endereco_prestador: str
    bairro_prestador: str
    cidade_prestador: str
    uf_prestador: str
    cep_prestador: str
    status_nfe: str
    tributacao_nfe: str
    opcao_simples: int
    codigo_servico: int
    aliquota_servicos: float
    valor_iss: int
    valor_credito: float
    iss_retido: bool
    discriminacao: str
    valor_servicos_centavos: int
    valor_deducoes_centavos: Optional[int] = None
    valor_pis_centavos: Optional[int] = None
    valor_cofins_centavos: Optional[int] = None
    valor_inss_centavos: Optional[int] = None
    valor_ir_centavos: Optional[int] = None
    valor_csll_centavos: Optional[int] = None
    cpf_cnpj_tomador: Optional[str] = None
    razao_social_tomador: Optional[str] = None
    tipo_logradouro_tomador: Optional[str] = None
    logradouro_tomador: Optional[str] = None
    numero_endereco_tomador: Optional[str] = None
    bairro_tomador: Optional[str] = None
    cidade_tomador: Optional[str] = None
    uf_tomador: Optional[str] = None
    cep_tomador: Optional[str] = None
    email_tomador: Optional[str] = None
    chave_rps_inscricao_prestador: Optional[str] = None
    chave_rps_serie_rps: Optional[str] = None
    chave_rps_numero_rps: Optional[int] = None
    tipo_rps: Optional[str] = None
    data_emissao_rps: Optional[date] = None
    email_prestador: Optional[str] = None
    data_cancelamento: Optional[date] = None
    numero_guia: Optional[str] = None
    data_quitacao_guia: Optional[date] = None
    cpf_cnpj_intermediario: Optional[str] = None
    inscricao_municipal_intermediario: Optional[str] = None
    iss_retido_intermediario: Optional[bool] = None
    email_intermediario: Optional[str] = None
    valor_carga_tributaria_centavos: Optional[int] = None
    fonte_carga_tributaria: Optional[str] = None
    percentual_carga_triutaria: Optional[float] = None
    codigo_cei: Optional[int] = None
    matricula_obra: Optional[int] = None
    municipio_prestacao: Optional[str] = None
    numero_encapsulamento: Optional[int] = None
    valor_total_recebido_centavos: Optional[int] = None

    def __post_init__(self):
        self.fonte_carga_tributaria = self.fonte_carga_tributaria or None

    @staticmethod
    def ler_xml(xml: ElementBase):
        return RetornoNFe(
            assinatura=find_text(xml, ".//Assinatura"),
            chave_nfe_inscricao_prestador=find_text(
                xml, ".//ChaveNFe/InscricaoPrestador"
            ),
            chave_nfe_numero_nfe=optional_int(find_text(xml, ".//ChaveNFe/NumeroNFe")),
            chave_nfe_codigo_verificacao=find_text(
                xml, ".//ChaveNFe/CodigoVerificacao"
            ),
            data_emissao_nfe=optional_date(find_text(xml, ".//DataEmissaoNFe")),
            chave_rps_inscricao_prestador=find_text(
                xml, ".//ChaveRPS/InscricaoPrestador"
            ),
            chave_rps_serie_rps=find_text(xml, ".//ChaveRPS/SerieRPS"),
            chave_rps_numero_rps=optional_int(find_text(xml, ".//ChaveRPS/NumeroRPS")),
            tipo_rps=find_text(xml, ".//TipoRPS"),
            data_emissao_rps=optional_date(find_text(xml, ".//DataEmissaoRPS")),
            cpf_cnpj_prestador=find_text(xml, ".//CPFCNPJPrestador/CNPJ"),
            razao_social_prestador=find_text(xml, ".//RazaoSocialPrestador"),
            tipo_logradouro_prestador=find_text(
                xml, ".//EnderecoPrestador/TipoLogradouro"
            ),
            logradouro_prestador=find_text(xml, ".//EnderecoPrestador/Logradouro"),
            numero_endereco_prestador=find_text(
                xml, ".//EnderecoPrestador/NumeroEndereco"
            ),
            complemento_endereco_prestador=find_text(
                xml, ".//EnderecoPrestador/ComplementoEndereco"
            ),
            bairro_prestador=find_text(xml, ".//EnderecoPrestador/Bairro"),
            cidade_prestador=find_text(xml, ".//EnderecoPrestador/Cidade"),
            uf_prestador=find_text(xml, ".//EnderecoPrestador/UF"),
            cep_prestador=find_text(xml, ".//EnderecoPrestador/CEP"),
            status_nfe=find_text(xml, ".//StatusNFe"),
            tributacao_nfe=find_text(xml, ".//TributacaoNFe"),
            opcao_simples=optional_int(find_text(xml, ".//OpcaoSimples")),
            valor_servicos_centavos=optional_int(find_text(xml, ".//ValorServicos")),
            valor_deducoes_centavos=optional_int(find_text(xml, ".//ValorDeducoes")),
            valor_pis_centavos=optional_int(find_text(xml, ".//ValorPIS")),
            valor_cofins_centavos=optional_int(find_text(xml, ".//ValorCOFINS")),
            valor_inss_centavos=optional_int(find_text(xml, ".//ValorINSS")),
            valor_ir_centavos=optional_int(find_text(xml, ".//ValorIR")),
            valor_csll_centavos=optional_int(find_text(xml, ".//ValorCSLL")),
            codigo_servico=optional_int(find_text(xml, ".//CodigoServico")),
            aliquota_servicos=optional_float(find_text(xml, ".//AliquotaServicos")),
            valor_iss=optional_int(find_text(xml, ".//ValorISS")),
            valor_credito=optional_float(find_text(xml, ".//ValorCredito")),
            iss_retido=optional_bool(find_text(xml, ".//ISSRetido")),
            cpf_cnpj_tomador=find_text(xml, ".//CPFCNPJTomador"),
            razao_social_tomador=find_text(xml, ".//RazaoSocialTomador"),
            tipo_logradouro_tomador=find_text(xml, ".//EnderecoTomador/TipoLogradouro"),
            logradouro_tomador=find_text(xml, ".//EnderecoTomador/Logradouro"),
            numero_endereco_tomador=find_text(xml, ".//EnderecoTomador/NumeroEndereco"),
            bairro_tomador=find_text(xml, ".//EnderecoTomador/Bairro"),
            cidade_tomador=find_text(xml, ".//EnderecoTomador/Cidade"),
            uf_tomador=find_text(xml, ".//EnderecoTomador/UF"),
            cep_tomador=find_text(xml, ".//EnderecoTomador/CEP"),
            email_tomador=find_text(xml, ".//EmailTomador"),
            discriminacao=find_text(xml, ".//Discriminacao"),
            fonte_carga_tributaria=find_text(xml, ".//FonteCargaTributaria"),
        )


@dataclass
class RetornoConsulta(Retorno):
    lista_nfe: List[RetornoNFe]

    @staticmethod
    def ler_xml(xml: ElementBase):
        sucesso = xml.find(".//Sucesso").text == "true"
        if sucesso:
            lista_nfe = []
            for nfe_xml in xml.findall(".//NFe"):
                lista_nfe.append(RetornoNFe.ler_xml(nfe_xml))
            return RetornoConsulta(lista_nfe=lista_nfe)
        else:
            raise Erro(
                codigo=int(xml.find(".//Codigo").text),
                descricao=xml.find(".//Descricao").text,
            )


@dataclass
class ConsultaNFe(Pedido, Remessa):
    chave_nfe_inscricao_prestador: str
    chave_nfe_numero_nfe: int
    chave_rps_inscricao_prestador: str
    chave_rps_serie_rps: str
    chave_rps_numero_rps: int
    chave_nfe_codigo_verificacao: Optional[str] = None
    """
    Código de verificação da NFe gerada pelo sistema de notas fiscais eletrônicas.
    """

    def __post_init__(self):
        if isinstance(self.chave_nfe_inscricao_prestador, int):
            self.chave_nfe_inscricao_prestador = str(self.chave_nfe_inscricao_prestador)
        self.chave_nfe_inscricao_prestador = self.chave_nfe_inscricao_prestador.zfill(8)
        assert (
            len(self.chave_nfe_inscricao_prestador) == 8
        ), f"A inscrição do prestador deve ter 8 caracteres. Recebido: {self.chave_nfe_inscricao_prestador}"

        if isinstance(self.chave_rps_inscricao_prestador, int):
            self.chave_rps_inscricao_prestador = str(self.chave_rps_inscricao_prestador)
        self.chave_rps_inscricao_prestador = self.chave_rps_inscricao_prestador.zfill(8)
        assert (
            len(self.chave_rps_inscricao_prestador) == 8
        ), f"A inscrição do prestador deve ter 8 caracteres. Recebido: {self.chave_rps_inscricao_prestador}"

        self.chave_nfe_codigo_verificacao = "".join(
            filter(str.isalnum, self.chave_nfe_codigo_verificacao)
        ).upper()
        assert (
            self.chave_nfe_codigo_verificacao is None
            or isinstance(self.chave_nfe_codigo_verificacao, str)
            and len(self.chave_nfe_codigo_verificacao) == 8
        ), f"O código de verificação deve ter 8 caracteres. Recebido: {self.chave_nfe_codigo_verificacao}"

    def gerar_xml(self, assinador: Assinador):
        xml = self.template.render(
            remetente=self.remetente,
            remetente_tipo=self.remetente_tipo,
            chave_nfe_inscricao_prestador=self.chave_nfe_inscricao_prestador,
            chave_nfe_numero_nfe=self.chave_nfe_numero_nfe,
            chave_rps_inscricao_prestador=self.chave_rps_inscricao_prestador,
            chave_rps_serie_rps=self.chave_rps_serie_rps,
            chave_rps_numero_rps=self.chave_rps_numero_rps,
            chave_nfe_codigo_verificacao=self.chave_nfe_codigo_verificacao,
        )
        return fromstring(xml.encode("utf-8"))

    @property
    def classe_retorno(self):
        return RetornoConsulta.__name__
