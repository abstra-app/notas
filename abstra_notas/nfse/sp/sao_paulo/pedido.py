from abc import ABC, abstractmethod
from abstra_notas.assinatura import Assinador
from .retorno import Retorno
from jinja2 import Template
from pathlib import Path


class Pedido(ABC):
    @property
    @abstractmethod
    def classe_retorno(self) -> Retorno:
        raise NotImplementedError

    @abstractmethod
    def gerar_xml(self, assinador: Assinador) -> str:
        raise NotImplementedError

    @property
    def template(self) -> Template:
        template_path = (
            Path(__file__).parent / "templates" / f"{self.__class__.__name__}.xml"
        )
        return Template(template_path.read_text())
