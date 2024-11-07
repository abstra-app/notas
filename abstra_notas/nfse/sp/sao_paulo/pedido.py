from abc import ABC, abstractmethod
from abstra_notas.assinatura import Assinador
from .retorno import Retorno
from .templates import load_template
from jinja2 import Template


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
        return load_template(self.__class__.__name__)
