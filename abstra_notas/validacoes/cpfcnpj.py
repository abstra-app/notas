from .cpf import cpf_valido, normalizar_cpf
from .cnpj import cnpj_valido, normalizar_cnpj
from typing import Literal


def cpf_ou_cnpj(valor: str) -> Literal["CPF", "CNPJ"]:
    if cpf_valido(valor):
        return "CPF"
    elif cnpj_valido(valor):
        return "CNPJ"
    else:
        raise ValueError("Valor não é um CPF ou CNPJ válido.")


def normalizar_cpf_ou_cnpj(valor: str):
    if cpf_valido(valor):
        return normalizar_cpf(valor)
    elif cnpj_valido(valor):
        return normalizar_cnpj(valor)
    else:
        raise ValueError("Valor não é um CPF ou CNPJ válido.")
