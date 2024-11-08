from .cpf import cpf_valido
from .cnpj import cnpj_valido
from typing import Literal


def cpf_ou_cnpj(valor: str) -> Literal["CPF", "CNPJ"]:
    if cpf_valido(valor):
        return "CPF"
    elif cnpj_valido(valor):
        return "CNPJ"
    else:
        raise ValueError("Valor não é um CPF ou CNPJ válido.")
