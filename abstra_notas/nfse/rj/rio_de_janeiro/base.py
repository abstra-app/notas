from abc import abstractmethod, ABC
from abstra_notas.assinatura import Assinador
from .templates import load_template
from zeep.plugins import HistoryPlugin
from zeep import Client, Transport, Settings
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from lxml.etree import tostring, fromstring, ElementBase
from pathlib import Path
from typing import Generic, TypeVar
from tempfile import mktemp
import ssl



T = TypeVar('T', bound='Envio')

# Adapta para o TLS antigo de forma a ser compatível com o servidor da prefeitura do Rio de Janeiro
class TLSAdapterCorrigido(HTTPAdapter):
    """Adaptador TLS corrigido para resolver problemas de SSL"""
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers("HIGH:!DH:!aNULL")
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.maximum_version = ssl.TLSVersion.TLSv1_3
        
        try:
            ctx.options |= ssl.OP_NO_COMPRESSION
        except AttributeError:
            pass
        
        self.poolmanager = PoolManager(
            num_pools=connections, 
            maxsize=maxsize, 
            block=block, 
            ssl_context=ctx
        )

class Envio(ABC, Generic[T]):
    def gerar_xml(self) -> ElementBase:

        xml = load_template(self.__class__.__name__).render(self.__dict__)
        return fromstring(xml.encode("utf-8"))
    
    @abstractmethod
    def nome_operacao(self):
        raise NotImplementedError("Subclasses must implement this method.")
    
    @abstractmethod
    def resposta(self, xml: ElementBase):
        """
        Método para processar a resposta do serviço e retornar um objeto de resposta.
        Deve ser implementado por subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")
    
    @property
    def schema_path(self) -> Path:
        return Path(__file__).parent / "schemas" / f"{self.nome_operacao()}.xsd"


    def executar(self, caminho_pfx: Path, senha_pfx: str, homologacao=False) -> T:
        assinador = Assinador(caminho_pfx, senha_pfx)
        try:
            history = HistoryPlugin()
            keyfile = Path(mktemp())
            keyfile.write_bytes(assinador.private_key_pem_bytes)
            certfile = Path(mktemp())
            certfile.write_bytes(assinador.cert_pem_bytes)

            xml = self.gerar_xml()
            session = Session()
            session.cert = (certfile, keyfile)
            session.verify = False

            session.mount('https://', TLSAdapterCorrigido())

            settings = Settings(strict=True, xml_huge_tree=True)
            transport = Transport(session=session, cache=None, timeout=500)

            if homologacao:
                url = "https://notacariocahom.rio.gov.br/WSNacional/nfse.asmx?wsdl"
            else:
                url= "https://notacarioca.rio.gov.br/WSNacional/nfse.asmx?wsdl"
            client = Client(
                url, transport=transport, settings=settings, plugins=[history]
            )

            # Assina o XML
            xml_assinado = xml
            #xml_assinado = assinador.assinar_xml(xml)

            request_tmp_path = Path(mktemp())
            request_tmp_path.write_text(tostring(xml_assinado, encoding=str), encoding="utf-8")
            #print(f"Request saved to: {request_tmp_path}")


            response: str = getattr(client.service, self.nome_operacao())( tostring(xml_assinado, encoding=str))

            response_temp_path = Path(mktemp())
            response_temp_path.write_text(response, encoding="utf-8")
            #print(f"Response saved to: {response_temp_path}")
            xml_resposta =  fromstring(response.encode("utf-8"))
            return self.resposta(xml_resposta)
        finally:
            if keyfile.exists():
                keyfile.unlink()
            if certfile.exists():
                certfile.unlink()