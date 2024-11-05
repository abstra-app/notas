from json import loads
from pathlib import Path


_cidades = None
def ler_cidades():
    global _cidades
    if _cidades is not None:
        return _cidades
    
    with open(Path(__file__).parent / "municipios.json") as f:
        _cidades = loads(f.read())
    return _cidades

def validar_codigo_cidade(codigo: int) -> bool:
    cidades = ler_cidades()
    return any(cidade["id"] == codigo for cidade in cidades)

def normalizar_uf(uf: str) -> str:
    cidades = ler_cidades()
    uf = uf.upper()
    assert any(cidade["regiao-imediata"]["regiao-intermediaria"]["UF"]["sigla"] == uf for cidade in cidades), "UF não encontrada. Insira uma UF válida no formato de sigla (ex: SP, RJ, MG, etc)"