from dataclasses import dataclass


@dataclass
class Erro(Exception):
    codigo: str
    descricao: str

    def __str__(self):
        return f"Erro {self.codigo}: {self.descricao}"

    @property
    def sucesso(self):
        return False
