def normalizar_cep(cep: str) -> str:
    cep_normalizado = cep.replace("-", "").replace(".", "")
    if len(cep_normalizado) < 8:
        cep_normalizado = "0" * (8 - len(cep_normalizado)) + cep_normalizado
    assert len(cep_normalizado) == 8, "CEP deve ter 8 dígitos"
    return cep_normalizado
