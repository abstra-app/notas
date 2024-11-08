from .pedido import Pedido
from .retorno import Retorno
from dataclasses import dataclass
from typing import Literal, Union
from lxml.etree import Element, fromstring
from abstra_notas.validacoes.cpfcnpj import cpf_ou_cnpj, normalizar_cpf_ou_cnpj
from .cliente import Cliente
from abstra_notas.assinatura import Assinador
import base64


@dataclass
class RetornoCancelamentoNFe(Retorno):
    sucesso: bool

    @staticmethod
    def ler_xml(xml: str):
        xml = fromstring(xml.encode("utf-8"))
        sucesso = xml.find(".//Sucesso").text
        if sucesso == "true":
            return RetornoCancelamentoNFeSucesso(sucesso=True)
        else:
            return RetornoCancelamentoNFeErro(
                sucesso=False,
                codigo=int(xml.find(".//Codigo").text),
                descricao=xml.find(".//Descricao").text,
            )


@dataclass
class RetornoCancelamentoNFeSucesso:
    sucesso: bool


@dataclass
class RetornoCancelamentoNFeErro:
    sucesso: bool
    codigo: int
    descricao: str


@dataclass
class CancelamentoNFe(Pedido):
    remetente: str
    transacao: str
    inscricao_prestador: str
    numero_nfe: int

    def __post_init__(self):
        self.remetente = normalizar_cpf_ou_cnpj(self.remetente)

    @property
    def remetente_tipo(self) -> Literal["CPF", "CNPJ"]:
        return cpf_ou_cnpj(self.remetente)

    def gerar_xml(self, assinador: Assinador) -> Element:
        xml = self.template.render(
            remetente=self.remetente,
            remetente_tipo=self.remetente_tipo,
            transacao=self.transacao,
            inscricao_prestador=self.inscricao_prestador,
            numero_nfe=self.numero_nfe,
            assinatura=self.assinatura(assinador),
        ).encode("utf-8")

        return fromstring(xml)

    def assinatura(self, assinador: Assinador) -> str:
        template = ""
        template += self.inscricao_prestador.zfill(8)
        template += str(self.numero_nfe).zfill(12)

        template_bytes = template.encode("ascii")

        signed_template = assinador.assinar_bytes_rsa_sh1(template_bytes)
        return base64.b64encode(signed_template).decode("ascii")

    @property
    def classe_retorno(self):
        return RetornoCancelamentoNFe

    @property
    def remetente_tipo(self) -> Literal["CPF", "CNPJ"]:
        return cpf_ou_cnpj(self.remetente)

    def executar(
        self, cliente: Cliente
    ) -> Union[RetornoCancelamentoNFeSucesso, RetornoCancelamentoNFeErro]:
        return cliente.executar(self)
