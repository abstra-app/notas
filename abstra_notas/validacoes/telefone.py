def normalizar_telefone(telefone: str) -> str:
    """
    Normaliza o número de telefone removendo caracteres não numéricos.
    
    Args:
        telefone (str): Número de telefone a ser normalizado.
        
    Returns:
        str: Número de telefone normalizado.
    """
    digitos = ''.join(filter(str.isdigit, telefone))
    if len(digitos) == 10:
        return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
    elif len(digitos) == 11:
        return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"
    elif len(digitos) < 10:
        raise ValueError(f"Número de telefone inválido '{telefone}'. Deve conter 10 ou 11 dígitos. Verifique se não está faltando o DDD.")
    else:
        raise ValueError(f"Número de telefone inválido '{telefone}'. Deve conter no máximo 11 dígitos. Verifique se não está adicionando DDI.")