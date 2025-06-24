from dataclasses import dataclass
from typing import Optional
from lxml.etree import Element, fromstring, ElementBase
from abstra_notas.validacoes.cpfcnpj import normalizar_cpf_ou_cnpj
from .pedido import Pedido
from .retorno import Retorno
from .remessa import Remessa
from .erro import Erro
from abstra_notas.assinatura import Assinador


@dataclass
class ConsultaCNPJ(Pedido, Remessa):
    cnpj: str
    
    def __post_init__(self):
        self.cnpj = normalizar_cpf_ou_cnpj(self.cnpj)
    
    def gerar_xml(self, assinador: Assinador) -> Element:
        xml = self.template.render(
            remetente=self.remetente,
            remetente_tipo="1" if self.remetente_tipo == "CPF" else "2",
            cnpj=self.cnpj,
        )
        return fromstring(xml.encode("utf-8"))

    @property
    def metodo(self) -> str:
        return "ConsultarCnpj"


@dataclass
class RetornoConsultaCNPJ(Retorno):
    cnpj: str
    inscricao_municipal: Optional[str]
    razao_social: Optional[str]
    nome_fantasia: Optional[str]
    endereco: Optional[str]
    email: Optional[str]
    
    @staticmethod
    def ler_xml(xml: ElementBase) -> "RetornoConsultaCNPJ":
        # Verifica se há erro na resposta
        lista_mensagens = xml.find(".//ListaMensagemRetorno")
        if lista_mensagens is not None:
            mensagem = lista_mensagens.find(".//MensagemRetorno")
            if mensagem is not None:
                raise ErroConsultaCNPJ(
                    codigo=mensagem.find(".//Codigo").text,
                    descricao=mensagem.find(".//Mensagem").text,
                )
        
        # Processa os dados do contribuinte
        contribuinte = xml.find(".//Contribuinte")
        if contribuinte is not None:
            return RetornoConsultaCNPJ(
                cnpj=contribuinte.find(".//Cnpj").text,
                inscricao_municipal=contribuinte.find(".//InscricaoMunicipal").text if contribuinte.find(".//InscricaoMunicipal") is not None else None,
                razao_social=contribuinte.find(".//RazaoSocial").text if contribuinte.find(".//RazaoSocial") is not None else None,
                nome_fantasia=contribuinte.find(".//NomeFantasia").text if contribuinte.find(".//NomeFantasia") is not None else None,
                endereco=contribuinte.find(".//Endereco").text if contribuinte.find(".//Endereco") is not None else None,
                email=contribuinte.find(".//Email").text if contribuinte.find(".//Email") is not None else None,
            )


@dataclass
class ErroConsultaCNPJ(Erro):
    codigo: str
    descricao: str
