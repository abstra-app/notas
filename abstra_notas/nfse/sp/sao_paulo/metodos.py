from .envio_pedido import PedidoEnvioRPS
from .envio_retorno import RetornoEnvioRPS
from .consulta_cnpj_pedido import PedidoConsultaCNPJ
from .consulta_cnpj_retorno import RetornoConsultaCNPJ
from .tipos_comuns import Cabecalho, CPFCNPJRemetente
from os import getenv
from dotenv import load_dotenv
from zeep import Client, Transport
from requests import Session
from abstra_notas.assinatura import Assinatura
from lxml.etree import tostring


load_dotenv()

cnpj_remetente = getenv("NFSE_CNPJ_REMETENTE")


def execute(req):
    cred = Assinatura()
    url = "https://nfe.prefeitura.sp.gov.br/ws/lotenfe.asmx?WSDL"
    xml = req.gerar_xml()
    with cred.cert_pem_file as cert_pem_file, cred.private_key_pem_file as private_key_pem_file:
        cert = (cert_pem_file.name, private_key_pem_file.name)
        session = Session()
        session.cert = cert
        transport = Transport(session=session, cache=None)
        client = Client(url, transport=transport)
        method = req.__class__.__name__.replace("Pedido", "")
        signed_xml = cred.assinar(xml)

        client_response = getattr(client.service, method)(
            1, tostring(signed_xml, encoding=str)
        )
        return client_response


def enviar_rps(nota: PedidoEnvioRPS) -> RetornoEnvioRPS:
    return execute(nota)


def consultar_cnpj(cnpj: str) -> RetornoConsultaCNPJ:
    pedido = PedidoConsultaCNPJ(
        cabecalho=Cabecalho(
            cpf_cnpj_remetente=CPFCNPJRemetente(
                tipo="CNPJ", numero=getenv("NFSE_CNPJ_REMETENTE")
            ),
        ),
        cnpj_contribuinte=cnpj,
    )
    return execute(pedido)
