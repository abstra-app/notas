def normalizar_inscricao_municipal(inscricao_municipal, optional=False):
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
    if codigo is None and optional:
        return None
    codigo = "".join(filter(str.isalnum, codigo)).upper()
    assert (
        codigo is None or isinstance(codigo, str) and len(codigo) == 8
    ), f"O código de verificação deve ter 8 caracteres. Recebido: {codigo}"
    return codigo
