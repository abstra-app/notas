from .pedido import Pedido
from .retorno import Retorno
from dataclasses import dataclass
from lxml.etree import Element, fromstring, ElementBase
from abstra_notas.assinatura import Assinador
from typing import Literal
from abstra_notas.validacoes.cpfcnpj import cpf_ou_cnpj, normalizar_cpf_ou_cnpj
from .remessa import Remessa
from .erro import Erro


@dataclass
class RetornoConsultaCNPJ(Retorno):
    inscricao_municipal: str
    emite_nfe: bool

    @staticmethod
    def ler_xml(xml: ElementBase) -> "RetornoConsultaCNPJ":
        sucesso = xml.find(".//Sucesso").text == "true"
        if sucesso:
            return RetornoConsultaCNPJ(
                inscricao_municipal=xml.find(".//InscricaoMunicipal").text,
                emite_nfe=xml.find(".//EmiteNFe").text == "true",
            )
        else:
            raise ErroConsultaCNPJ(
                codigo=int(xml.find(".//Codigo").text),
                descricao=xml.find(".//Descricao").text,
            )


@dataclass
class ErroConsultaCNPJ(Erro):
    codigo: int
    descricao: str


@dataclass
class ConsultaCNPJ(Pedido, Remessa):
    contribuinte: str

    def __post_init__(self):
        self.contribuinte = normalizar_cpf_ou_cnpj(self.contribuinte)

    def gerar_xml(self, assinador: Assinador) -> Element:
        xml = self.template.render(
            remetente=self.remetente,
            contribuinte=self.contribuinte,
            contribuinte_tipo=self.contribuinte_tipo,
            remetente_tipo=self.remetente_tipo,
        )
        return fromstring(xml)

    @property
    def contribuinte_tipo(self) -> Literal["CPF", "CNPJ"]:
        return cpf_ou_cnpj(self.contribuinte)
