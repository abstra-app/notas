from dataclasses import dataclass
from .tipos_comuns import Cabecalho, CPFCNPJRemetente

# from xml.etree.ElementTree import Element, SubElement, tostring
from lxml.etree import Element, SubElement, tostring, indent
from abstra_notas.validacoes.cnpj import normalizar_cnpj

"""
<?xml version="1.0" encoding="UTF-8"?>
<p1:PedidoConsultaCNPJ xmlns:p1="http://www.prefeitura.sp.gov.br/nfe" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <Cabecalho Versao="1">
    <CPFCNPJRemetente>
      <CNPJ>99999997000100</CNPJ>
    </CPFCNPJRemetente>
  </Cabecalho>
  <CNPJContribuinte>
    <CNPJ>99999997000100</CNPJ>
  </CNPJContribuinte>
</p1:PedidoConsultaCNPJ>
"""


@dataclass
class PedidoConsultaCNPJ:
    cabecalho: Cabecalho
    cnpj_contribuinte: str

    def __post_init__(self):
        self.cnpj_contribuinte = normalizar_cnpj(self.cnpj_contribuinte)

    def gerar_xml(self):
        pedido_consulta_cnpj = Element(
            "PedidoConsultaCNPJ", xmlns="http://www.prefeitura.sp.gov.br/nfe"
        )
        cabecalho = self.cabecalho.gerar_xml()
        pedido_consulta_cnpj.append(cabecalho)
        cnpj_contribuinte = Element("CNPJContribuinte", xmlns="")
        SubElement(cnpj_contribuinte, "CNPJ").text = self.cnpj_contribuinte
        pedido_consulta_cnpj.append(cnpj_contribuinte)
        return pedido_consulta_cnpj

    @staticmethod
    def parse_xml(element: Element) -> "PedidoConsultaCNPJ":
        cabecalho = Cabecalho.parse_xml(element.find("Cabecalho"))
        cnpj_contribuinte = element.find("CNPJContribuinte").find("CNPJ").text
        return PedidoConsultaCNPJ(
            cabecalho=cabecalho, cnpj_contribuinte=cnpj_contribuinte
        )

    def gerar_string(self) -> str:
        xml = self.gerar_xml()
        indent(xml, space="  ")
        return tostring(xml, method="xml", encoding="unicode")
