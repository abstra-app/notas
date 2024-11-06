from dataclasses import dataclass
from typing import Literal
from lxml.etree import Element, SubElement
from abstra_notas.validacoes.cnpj import normalizar_cnpj
from abstra_notas.validacoes.cpf import normalizar_cpf


@dataclass
class CPFCNPJRemetente:
    tipo: Literal["CPF", "CNPJ"]
    numero: str

    def __post_init__(self):
        if self.tipo == "CPF":
            self.numero = normalizar_cpf(self.numero)
        if self.tipo == "CNPJ":
            self.numero = normalizar_cnpj(self.numero)

    def gerar_xml(self) -> Element:
        cpfcnpjremetente = Element("CPFCNPJRemetente")
        SubElement(cpfcnpjremetente, self.tipo).text = self.numero
        return cpfcnpjremetente

    @staticmethod
    def parse_xml(element: Element) -> "CPFCNPJRemetente":
        tipo = element[0].tag
        numero = element.find(tipo).text
        return CPFCNPJRemetente(tipo=tipo, numero=numero)


@dataclass
class Cabecalho:
    cpf_cnpj_remetente: CPFCNPJRemetente

    def gerar_xml(self) -> Element:
        cabecalho = Element("Cabecalho", xmlns="")
        cabecalho.set("Versao", "1")
        cpfcnpjremetente = self.cpf_cnpj_remetente.gerar_xml()
        cabecalho.append(cpfcnpjremetente)
        return cabecalho

    @staticmethod
    def parse_xml(element: Element) -> "Cabecalho":
        cpf_cnpj_remetente = CPFCNPJRemetente.parse_xml(
            element.find("CPFCNPJRemetente")
        )
        return Cabecalho(cpf_cnpj_remetente=cpf_cnpj_remetente)
