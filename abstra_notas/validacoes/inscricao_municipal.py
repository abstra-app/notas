def normalizar_inscricao_municipal(inscricao: str) -> str:
    """
    Normaliza a inscrição municipal, removendo caracteres não numéricos.
    """
    return ''.join(filter(str.isdigit, inscricao))