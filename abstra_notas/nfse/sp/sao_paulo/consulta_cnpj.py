from .pedido import Pedido
from dataclasses import dataclass
from lxml.etree import Element
from abstra_notas.assinatura import Assinador
from typing import Literal


@dataclass
class RetornoConsultaCNPJ:
    sucesso: bool
    inscricao_municipal: str
    emite_nfe: bool

    @staticmethod
    def ler_xml(xml: Element) -> "RetornoConsultaCNPJ":
        return RetornoConsultaCNPJ(
            sucesso=xml.find(".//Sucesso").text == "true",
            inscricao_municipal=xml.find(".//InscricaoMunicipal").text,
            emite_nfe=xml.find(".//EmiteNFe").text == "true",
        )


@dataclass
class PedidoConsultaCNPJ(Pedido):
    remetente: str
    contribuinte: str

    remetente_tipo: Literal["CPF", "CNPJ"]
    contribuinte_tipo: Literal["CPF", "CNPJ"]

    @property
    def classe_retorno(self) -> RetornoConsultaCNPJ:
        return RetornoConsultaCNPJ

    def gerar_xml(self, assinador: Assinador):
        xml = self.template.render(
            remetente=self.remetente,
            contribuinte=self.contribuinte,
        )

        return xml
