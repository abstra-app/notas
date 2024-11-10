from dataclasses import dataclass
from typing import Literal
from abstra_notas.validacoes.cpfcnpj import normalizar_cpf_ou_cnpj, cpf_ou_cnpj


@dataclass
class Remessa:
    remetente: str

    def __post_init__(self):
        self.remetente = normalizar_cpf_ou_cnpj(self.remetente)

    @property
    def remetente_tipo(self) -> Literal["CPF", "CNPJ"]:
        return cpf_ou_cnpj(self.remetente)
