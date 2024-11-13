from abc import ABC, abstractmethod
from abstra_notas.assinatura import Assinador
from lxml.etree import ElementBase
from .templates import load_template
from jinja2 import Template


class Pedido(ABC):
    @abstractmethod
    def gerar_xml(self, assinador: Assinador) -> ElementBase:
        raise NotImplementedError

    @property
    def template(self) -> Template:
        return load_template(self.__class__.__name__)

    @property
    def metodo(self) -> str:
        return self.__class__.__name__.replace("Pedido", "")

    @property
    def classe_retorno(self):
        return f"Retorno{self.__class__.__name__}"
