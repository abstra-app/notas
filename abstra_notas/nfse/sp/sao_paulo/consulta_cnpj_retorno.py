from dataclasses import dataclass
from .retorno import Retorno
from lxml.etree import Element, SubElement, ElementBase
from .erro import Erro


@dataclass
class Detalhe:
    inscricao_municipal: str
    emite_nfse: bool

    def gerar_xml(self):
        detalhe = Element("Detalhe")
        SubElement(detalhe, "InscricaoMunicipal").text = self.inscricao_municipal
        SubElement(detalhe, "EmiteNFSe").text = "true" if self.emite_nfse else "false"
        return detalhe

    @staticmethod
    def parse_xml(element: ElementBase) -> "Detalhe":
        inscricao_municipal = element.find("InscricaoMunicipal").text
        emite_nfse = element.find("EmiteNFSe").text == "true"
        return Detalhe(inscricao_municipal=inscricao_municipal, emite_nfse=emite_nfse)


@dataclass
class RetornoConsultaCNPJ(Retorno):
    detalhe: Detalhe

    def gerar_xml(self):
        retorno_consulta_cnpj = ElementBase(
            "p1:RetornoConsultaCNPJ",
            nsmap={
                "p1": "http://www.prefeitura.sp.gov.br/nfe",
                "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            },
        )
        SubElement(retorno_consulta_cnpj, "Sucesso").text = (
            "true" if self.sucesso else "false"
        )
        detalhe = self.detalhe.gerar_xml()
        retorno_consulta_cnpj.append(detalhe)
        return retorno_consulta_cnpj

    @staticmethod
    def parse_xml(element: ElementBase) -> "RetornoConsultaCNPJ":
        sucesso = element.find("Sucesso").text == "true"
        if not sucesso:
            raise Erro(
                codigo=int(element.find("Codigo").text),
                descricao=element.find("Descricao").text,
            )
        detalhe = Detalhe.parse_xml(element.find("Detalhe"))
        return RetornoConsultaCNPJ(detalhe=detalhe)
