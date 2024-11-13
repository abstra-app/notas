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


@dataclass
class RetornoNFe:
    assinatura: str
    chave_nfe_inscricao_prestador: str
    chave_nfe_numero_nfe: int
    chave_nfe_codigo_verificacao: str
    data_emissao_nfe: date
    chave_rps_inscricao_prestador: str
    chave_rps_serie_rps: str
    chave_rps_numero_rps: int
    tipo_rps: str
    data_emissao_rps: date
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
    valor_servicos: int
    valor_deducoes: int
    valor_pis: int
    valor_cofins: int
    valor_inss: int
    valor_ir: int
    valor_csll: int
    codigo_servico: int
    aliquota_servicos: float
    valor_iss: int
    valor_credito: float
    iss_retido: bool
    cpf_cnpj_tomador: str
    razao_social_tomador: str
    tipo_logradouro_tomador: str
    logradouro_tomador: str
    numero_endereco_tomador: str
    bairro_tomador: str
    cidade_tomador: str
    uf_tomador: str
    cep_tomador: str
    email_tomador: str
    discriminacao: str
    fonte_carga_tributaria: str

    def __post_init__(self):
        self.fonte_carga_tributaria = self.fonte_carga_tributaria or None

    @staticmethod
    def ler_xml(xml: ElementBase):
        return RetornoNFe(
            assinatura=xml.find(".//Assinatura").text,
            chave_nfe_inscricao_prestador=xml.find(
                ".//ChaveNFe/InscricaoPrestador"
            ).text,
            chave_nfe_numero_nfe=int(xml.find(".//ChaveNFe/NumeroNFe").text),
            chave_nfe_codigo_verificacao=xml.find(".//ChaveNFe/CodigoVerificacao").text,
            data_emissao_nfe=parse(xml.find(".//DataEmissaoNFe").text).date(),
            chave_rps_inscricao_prestador=xml.find(
                ".//ChaveRPS/InscricaoPrestador"
            ).text,
            chave_rps_serie_rps=xml.find(".//ChaveRPS/SerieRPS").text,
            chave_rps_numero_rps=int(xml.find(".//ChaveRPS/NumeroRPS").text),
            tipo_rps=xml.find(".//TipoRPS").text,
            data_emissao_rps=parse(xml.find(".//DataEmissaoRPS").text).date(),
            cpf_cnpj_prestador=xml.find(".//CPFCNPJPrestador/CNPJ").text,
            razao_social_prestador=xml.find(".//RazaoSocialPrestador").text,
            tipo_logradouro_prestador=xml.find(
                ".//EnderecoPrestador/TipoLogradouro"
            ).text,
            logradouro_prestador=xml.find(".//EnderecoPrestador/Logradouro").text,
            numero_endereco_prestador=xml.find(
                ".//EnderecoPrestador/NumeroEndereco"
            ).text,
            complemento_endereco_prestador=xml.find(
                ".//EnderecoPrestador/ComplementoEndereco"
            ).text,
            bairro_prestador=xml.find(".//EnderecoPrestador/Bairro").text,
            cidade_prestador=xml.find(".//EnderecoPrestador/Cidade").text,
            uf_prestador=xml.find(".//EnderecoPrestador/UF").text,
            cep_prestador=xml.find(".//EnderecoPrestador/CEP").text,
            status_nfe=xml.find(".//StatusNFe").text,
            tributacao_nfe=xml.find(".//TributacaoNFe").text,
            opcao_simples=int(xml.find(".//OpcaoSimples").text),
            valor_servicos=int(xml.find(".//ValorServicos").text),
            valor_deducoes=int(xml.find(".//ValorDeducoes").text),
            valor_pis=int(xml.find(".//ValorPIS").text),
            valor_cofins=int(xml.find(".//ValorCOFINS").text),
            valor_inss=int(xml.find(".//ValorINSS").text),
            valor_ir=int(xml.find(".//ValorIR").text),
            valor_csll=int(xml.find(".//ValorCSLL").text),
            codigo_servico=int(xml.find(".//CodigoServico").text),
            aliquota_servicos=float(xml.find(".//AliquotaServicos").text),
            valor_iss=int(xml.find(".//ValorISS").text),
            valor_credito=float(xml.find(".//ValorCredito").text),
            iss_retido=xml.find(".//ISSRetido").text == "true",
            cpf_cnpj_tomador=xml.find(".//CPFCNPJTomador/CPF").text,
            razao_social_tomador=xml.find(".//RazaoSocialTomador").text,
            tipo_logradouro_tomador=xml.find(".//EnderecoTomador/TipoLogradouro").text,
            logradouro_tomador=xml.find(".//EnderecoTomador/Logradouro").text,
            numero_endereco_tomador=xml.find(".//EnderecoTomador/NumeroEndereco").text,
            bairro_tomador=xml.find(".//EnderecoTomador/Bairro").text,
            cidade_tomador=xml.find(".//EnderecoTomador/Cidade").text,
            uf_tomador=xml.find(".//EnderecoTomador/UF").text,
            cep_tomador=xml.find(".//EnderecoTomador/CEP").text,
            email_tomador=xml.find(".//EmailTomador").text,
            discriminacao=xml.find(".//Discriminacao").text,
            fonte_carga_tributaria=xml.find(".//FonteCargaTributaria").text,
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

        if isinstance(self.chave_nfe_codigo_verificacao, int):
            self.chave_nfe_codigo_verificacao = str(self.chave_nfe_codigo_verificacao)

        assert (
            self.chave_nfe_codigo_verificacao is None
            or len(self.chave_nfe_codigo_verificacao) == 8
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
