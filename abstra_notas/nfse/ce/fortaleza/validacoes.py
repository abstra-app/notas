def normalizar_inscricao_municipal(inscricao_municipal, optional=False):
    """
    Normaliza a inscrição municipal para Fortaleza.
    Fortaleza usa inscrição municipal de 8 dígitos.
    """
    if inscricao_municipal is None and optional:
        return None
    if isinstance(inscricao_municipal, int):
        inscricao_municipal = str(inscricao_municipal)
    inscricao_municipal = inscricao_municipal.zfill(8)
    assert (
        len(inscricao_municipal) == 8
    ), f"A inscrição deve ter 8 caracteres. Recebido: {inscricao_municipal}"
    return inscricao_municipal


def normalizar_codigo_verificacao(codigo, optional=False):
    """
    Normaliza o código de verificação da NFSe.
    """
    if codigo is None and optional:
        return None
    if codigo:
        codigo = "".join(filter(str.isalnum, codigo)).upper()
        assert (
            len(codigo) <= 15
        ), f"O código de verificação deve ter no máximo 15 caracteres. Recebido: {codigo}"
    return codigo


def normalizar_data(data):
    """
    Normaliza uma data para string no formato YYYY-MM-DD.
    """
    if isinstance(data, str):
        return data
    return data.strftime("%Y-%m-%d")
