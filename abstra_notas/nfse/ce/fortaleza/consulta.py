from dataclasses import dataclass
from typing import Optional, List
from lxml.etree import Element, fromstring, ElementBase
from datetime import date
from dateutil.parser import parse
from abstra_notas.assinatura import Assinador
from .pedido import Pedido
from .retorno import Retorno
from .remessa import Remessa
from .erro import Erro
from .validacoes import normalizar_inscricao_municipal, normalizar_codigo_verificacao, normalizar_data


@dataclass
class ConsultaNFe(Pedido, Remessa):
    numero_nfse: Optional[int] = None
    codigo_verificacao: Optional[str] = None
    numero_rps: Optional[int] = None
    serie_rps: Optional[str] = None
    inscricao_prestador: Optional[str] = None
    
    def __post_init__(self):
        if self.inscricao_prestador:
            self.inscricao_prestador = normalizar_inscricao_municipal(self.inscricao_prestador)
        if self.codigo_verificacao:
            self.codigo_verificacao = normalizar_codigo_verificacao(self.codigo_verificacao)

    def gerar_xml(self, assinador: Assinador) -> Element:
        xml = self.template.render(
            remetente=self.remetente,
            remetente_tipo="1" if self.remetente_tipo == "CPF" else "2",
            numero_nfse=self.numero_nfse,
            codigo_verificacao=self.codigo_verificacao,
            numero_rps=self.numero_rps,
            serie_rps=self.serie_rps,
            inscricao_prestador=self.inscricao_prestador,
        )
        return fromstring(xml.encode("utf-8"))

    @property
    def metodo(self) -> str:
        return "ConsultarNfsePorRps"


@dataclass
class ConsultaNFePeriodo(Pedido, Remessa):
    data_inicio: date
    data_fim: date
    inscricao_prestador: Optional[str] = None
    pagina: int = 1
    
    def __post_init__(self):
        if self.inscricao_prestador:
            self.inscricao_prestador = normalizar_inscricao_municipal(self.inscricao_prestador)
        self.data_inicio = normalizar_data(self.data_inicio)
        self.data_fim = normalizar_data(self.data_fim)

    def gerar_xml(self, assinador: Assinador) -> Element:
        xml = self.template.render(
            remetente=self.remetente,
            remetente_tipo="1" if self.remetente_tipo == "CPF" else "2",
            data_inicio=self.data_inicio,
            data_fim=self.data_fim,
            inscricao_prestador=self.inscricao_prestador,
            pagina=self.pagina,
        )
        return fromstring(xml.encode("utf-8"))

    @property
    def metodo(self) -> str:
        return "ConsultarNfseServicoPrestado"


@dataclass
class RetornoNFe:
    numero_nfse: int
    codigo_verificacao: str
    data_emissao: date
    numero_rps: Optional[int] = None
    serie_rps: Optional[str] = None
    prestador_cnpj: Optional[str] = None
    prestador_inscricao_municipal: Optional[str] = None
    prestador_razao_social: Optional[str] = None
    tomador_cnpj_cpf: Optional[str] = None
    tomador_razao_social: Optional[str] = None
    valor_servicos: Optional[float] = None
    valor_deducoes: Optional[float] = None
    codigo_servico: Optional[str] = None
    discriminacao: Optional[str] = None
    iss_retido: Optional[bool] = None
    aliquota: Optional[float] = None


@dataclass
class RetornoConsulta(Retorno):
    lista_nfse: List[RetornoNFe]
    
    @staticmethod
    def ler_xml(xml: ElementBase) -> "RetornoConsulta":
        # Verifica se há erro na resposta
        lista_mensagens = xml.find(".//ListaMensagemRetorno")
        if lista_mensagens is not None:
            mensagem = lista_mensagens.find(".//MensagemRetorno")
            if mensagem is not None:
                raise ErroConsulta(
                    codigo=mensagem.find(".//Codigo").text,
                    descricao=mensagem.find(".//Mensagem").text,
                )
        
        # Processa a lista de NFSe
        lista_nfse = []
        nfses = xml.findall(".//CompNfse")
        for nfse_elem in nfses:
            nfse = nfse_elem.find(".//Nfse/InfNfse")
            if nfse is not None:
                lista_nfse.append(RetornoNFe(
                    numero_nfse=int(nfse.find(".//Numero").text),
                    codigo_verificacao=nfse.find(".//CodigoVerificacao").text,
                    data_emissao=parse(nfse.find(".//DataEmissao").text).date(),
                    numero_rps=int(nfse.find(".//DeclaracaoPrestacaoServico/InfDeclaracaoPrestacaoServico/Rps/IdentificacaoRps/Numero").text) if nfse.find(".//DeclaracaoPrestacaoServico/InfDeclaracaoPrestacaoServico/Rps/IdentificacaoRps/Numero") is not None else None,
                    serie_rps=nfse.find(".//DeclaracaoPrestacaoServico/InfDeclaracaoPrestacaoServico/Rps/IdentificacaoRps/Serie").text if nfse.find(".//DeclaracaoPrestacaoServico/InfDeclaracaoPrestacaoServico/Rps/IdentificacaoRps/Serie") is not None else None,
                    prestador_cnpj=nfse.find(".//PrestadorServico/IdentificacaoPrestador/Cnpj").text if nfse.find(".//PrestadorServico/IdentificacaoPrestador/Cnpj") is not None else None,
                    prestador_inscricao_municipal=nfse.find(".//PrestadorServico/IdentificacaoPrestador/InscricaoMunicipal").text if nfse.find(".//PrestadorServico/IdentificacaoPrestador/InscricaoMunicipal") is not None else None,
                    prestador_razao_social=nfse.find(".//PrestadorServico/RazaoSocial").text if nfse.find(".//PrestadorServico/RazaoSocial") is not None else None,
                    tomador_cnpj_cpf=nfse.find(".//TomadorServico/IdentificacaoTomador/CpfCnpj/Cnpj").text or nfse.find(".//TomadorServico/IdentificacaoTomador/CpfCnpj/Cpf").text if nfse.find(".//TomadorServico/IdentificacaoTomador/CpfCnpj") is not None else None,
                    tomador_razao_social=nfse.find(".//TomadorServico/RazaoSocial").text if nfse.find(".//TomadorServico/RazaoSocial") is not None else None,
                    valor_servicos=float(nfse.find(".//Servico/Valores/ValorServicos").text) if nfse.find(".//Servico/Valores/ValorServicos") is not None else None,
                    valor_deducoes=float(nfse.find(".//Servico/Valores/ValorDeducoes").text) if nfse.find(".//Servico/Valores/ValorDeducoes") is not None else None,
                    codigo_servico=nfse.find(".//Servico/CodigoTributacaoMunicipio").text if nfse.find(".//Servico/CodigoTributacaoMunicipio") is not None else None,
                    discriminacao=nfse.find(".//Servico/Discriminacao").text if nfse.find(".//Servico/Discriminacao") is not None else None,
                    iss_retido=nfse.find(".//Servico/Valores/IssRetido").text == "1" if nfse.find(".//Servico/Valores/IssRetido") is not None else None,
                    aliquota=float(nfse.find(".//Servico/Valores/Aliquota").text) / 100 if nfse.find(".//Servico/Valores/Aliquota") is not None else None,
                ))
        
        return RetornoConsulta(lista_nfse=lista_nfse)


@dataclass
class ErroConsulta(Erro):
    codigo: str
    descricao: str
