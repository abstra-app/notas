from dataclasses import dataclass
from lxml.etree import Element, fromstring, ElementBase
from abstra_notas.assinatura import Assinador
from .pedido import Pedido
from .retorno import Retorno
from .remessa import Remessa
from .erro import Erro
from .validacoes import normalizar_inscricao_municipal


@dataclass
class CancelamentoNFe(Pedido, Remessa):
    inscricao_prestador: str
    numero_nfse: int
    codigo_cancelamento: str
    """
    Código do motivo do cancelamento:
    1 - Erro na emissão
    2 - Serviço não prestado
    3 - Erro de dados
    4 - Duplicidade
    """
    
    def __post_init__(self):
        self.inscricao_prestador = normalizar_inscricao_municipal(self.inscricao_prestador)

    def gerar_xml(self, assinador: Assinador) -> Element:
        xml = self.template.render(
            remetente=self.remetente,
            remetente_tipo="1" if self.remetente_tipo == "CPF" else "2",
            inscricao_prestador=self.inscricao_prestador,
            numero_nfse=self.numero_nfse,
            codigo_cancelamento=self.codigo_cancelamento,
        )
        return fromstring(xml.encode("utf-8"))

    @property
    def metodo(self) -> str:
        return "CancelarNfse"


@dataclass
class RetornoCancelamentoNFe(Retorno):
    numero_nfse: int
    codigo_verificacao: str
    data_cancelamento: str
    
    @staticmethod
    def ler_xml(xml: ElementBase) -> "RetornoCancelamentoNFe":
        # Verifica se há erro na resposta
        lista_mensagens = xml.find(".//ListaMensagemRetorno")
        if lista_mensagens is not None:
            mensagem = lista_mensagens.find(".//MensagemRetorno")
            if mensagem is not None:
                raise ErroCancelamentoNFe(
                    codigo=mensagem.find(".//Codigo").text,
                    descricao=mensagem.find(".//Mensagem").text,
                )
        
        # Processa o cancelamento
        cancelamento = xml.find(".//RetCancelamento")
        if cancelamento is not None:
            nfse = cancelamento.find(".//NfseCancelamento")
            if nfse is not None:
                return RetornoCancelamentoNFe(
                    numero_nfse=int(nfse.find(".//Numero").text),
                    codigo_verificacao=nfse.find(".//CodigoVerificacao").text,
                    data_cancelamento=nfse.find(".//DataCancelamento").text,
                )


@dataclass
class ErroCancelamentoNFe(Erro):
    codigo: str
    descricao: str
