from typing import Union


def normalizar_cep(cep: Union[str, int]) -> str:
    cep = str(cep)
    cep = cep.replace("-", "").replace(".", "")
    assert cep.isdigit(), "CEP deve conter apenas números"
    cep = cep.zfill(8)
    assert len(cep) == 8, "CEP deve conter 8 dígitos"
    return cep
