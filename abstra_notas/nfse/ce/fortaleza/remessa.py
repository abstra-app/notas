from dataclasses import dataclass
from typing import Literal
from abstra_notas.validacoes.cpfcnpj import normalizar_cpf_ou_cnpj, cpf_ou_cnpj


@dataclass
class Remessa:
    remetente: str
    """
    CPF ou CNPJ do remetente (prestador de serviços). Qualquer formato é aceito, ex: 00000000000, 00.000.000/0000-00.
    """

    def __post_init__(self):
        self.remetente = normalizar_cpf_ou_cnpj(self.remetente)

    @property
    def remetente_tipo(self) -> Literal["CPF", "CNPJ"]:
        return cpf_ou_cnpj(self.remetente)
