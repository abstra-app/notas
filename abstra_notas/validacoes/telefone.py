def normalizar_validar_telefone(telefone: str) -> str:
    """
    Normaliza o número de telefone removendo caracteres não numéricos.
    
    Args:
        telefone (str): Número de telefone a ser normalizado.
        
    Returns:
        str: Número de telefone normalizado.
    """
    digitos = "".join(t for t in telefone if t.isdigit())
    if len(digitos) == 10 or len(digitos) == 11:
        return digitos
    elif len(digitos) == 0:
        return digitos
    elif len(digitos) < 10:
        raise ValueError(f"Número de telefone inválido '{telefone}'. Deve conter 10 ou 11 dígitos. Verifique se não está faltando o DDD.")
    else:
        raise ValueError(f"Número de telefone inválido '{telefone}'. Deve conter no máximo 11 dígitos. Verifique se não está adicionando DDI.")