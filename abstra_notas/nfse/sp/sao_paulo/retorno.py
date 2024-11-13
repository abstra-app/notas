from abc import ABC, abstractmethod


class Retorno(ABC):
    @staticmethod
    @abstractmethod
    def ler_xml(xml: str) -> "Retorno":
        raise NotImplementedError

    @property
    def sucesso(self) -> bool:
        return True
