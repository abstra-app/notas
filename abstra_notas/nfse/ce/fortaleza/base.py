from abc import abstractmethod, ABC
from abstra_notas.assinatura import Assinador
from .templates import load_template
from zeep.plugins import HistoryPlugin
from zeep import Client, Transport, Settings
from requests import Session
from lxml.etree import tostring, fromstring, ElementBase
from pathlib import Path
from typing import Generic, TypeVar
from tempfile import mktemp

T = TypeVar('T', bound='Envio')

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


    def executar(self, caminho_pfx: Path, senha_pfx: str) -> T:
        assinador = Assinador(caminho_pfx, senha_pfx)
        try:
            history = HistoryPlugin()
            keyfile = Path(mktemp())
            keyfile.write_bytes(assinador.private_key_pem_bytes)
            certfile = Path(mktemp())
            certfile.write_bytes(assinador.cert_pem_bytes)
            url = "https://iss.fortaleza.ce.gov.br/grpfor-iss/ServiceGinfesImplService?wsdl"
            xml = self.gerar_xml()
            request_tmp_path = Path(mktemp())
            request_tmp_path.write_text(tostring(xml, encoding=str), encoding="utf-8")
            print(f"Request saved to: {request_tmp_path}")
            session = Session()
            session.cert = (certfile, keyfile)
            session.verify = False
            settings = Settings(strict=True, xml_huge_tree=True)
            transport = Transport(session=session, cache=None)
            client = Client(
                url, transport=transport, settings=settings, plugins=[history]
            )
            signed_xml = assinador.assinar_xml(xml)

            response: str = getattr(client.service, self.nome_operacao())(
                1, tostring(signed_xml, encoding=str)
            )

            response_temp_path = Path(mktemp())
            response_temp_path.write_text(response, encoding="utf-8")
            print(f"Response saved to: {response_temp_path}")
            xml_resposta =  fromstring(response.encode("utf-8"))
            return self.resposta(xml_resposta)
        finally:
            keyfile.unlink()
            certfile.unlink()