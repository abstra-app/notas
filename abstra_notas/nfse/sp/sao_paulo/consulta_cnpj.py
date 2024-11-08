from .pedido import Pedido
from .retorno import Retorno
from dataclasses import dataclass
from .cliente import Cliente
from lxml.etree import Element, fromstring
from abstra_notas.assinatura import Assinador
from typing import Literal, Union
from abstra_notas.validacoes.cpfcnpj import cpf_ou_cnpj, normalizar_cpf_ou_cnpj

@dataclass
class RetornoConsultaCNPJ(Retorno):
    sucesso: bool

    @staticmethod
    def ler_xml(xml: Element) -> "RetornoConsultaCNPJ":
        xml = fromstring(xml.encode("utf-8"))
        if xml.find(".//Sucesso").text == "true":
            return RetornoConsultaCNPJSucesso.ler_xml(xml)
        else:
            return RetornoConsultaCNPJErro.ler_xml(xml)


@dataclass
class RetornoConsultaCNPJSucesso(RetornoConsultaCNPJ):
    inscricao_municipal: str
    emite_nfe: bool

    @staticmethod
    def ler_xml(xml: str) -> "RetornoConsultaCNPJSucesso":
        return RetornoConsultaCNPJSucesso(
            sucesso=True,
            inscricao_municipal=xml.find(".//InscricaoMunicipal").text,
            emite_nfe=xml.find(".//EmiteNFe").text == "true",
        )

@dataclass
class RetornoConsultaCNPJErro(RetornoConsultaCNPJ):
    codigo: int
    descricao: str

    @staticmethod
    def ler_xml(xml: Element) -> "RetornoConsultaCNPJErro":
        return RetornoConsultaCNPJErro(
            sucesso=False,
            codigo=int(xml.find(".//Codigo").text),
            descricao=xml.find(".//Descricao").text,
        )


@dataclass
class ConsultaCNPJ(Pedido):
    remetente: str
    contribuinte: str

    def __post_init__(self):
        self.remetente = normalizar_cpf_ou_cnpj(self.remetente)
        self.contribuinte = normalizar_cpf_ou_cnpj(self.contribuinte)


    @property
    def classe_retorno(self) -> RetornoConsultaCNPJ:
        return RetornoConsultaCNPJ

    def gerar_xml(self, assinador: Assinador) -> Element:
        xml = self.template.render(
            remetente=self.remetente,
            contribuinte=self.contribuinte,
            contribuinte_tipo=self.contribuinte_tipo,
            remetente_tipo=self.remetente_tipo,
        )
        return fromstring(xml)


    @property
    def remetente_tipo(self) -> Literal["CPF", "CNPJ"]:
        return cpf_ou_cnpj(self.remetente)
    
    @property
    def contribuinte_tipo(self) -> Literal["CPF", "CNPJ"]:
        return cpf_ou_cnpj(self.contribuinte)
    
    def executar(self, cliente: Cliente) -> Union[RetornoConsultaCNPJSucesso, RetornoConsultaCNPJErro]:
        return cliente.executar(self)