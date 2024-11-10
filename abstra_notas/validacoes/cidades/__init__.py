from json import loads
from pathlib import Path
from enum import Enum


_cidades = None


def ler_cidades():
    global _cidades
    if _cidades is not None:
        return _cidades

    with open(Path(__file__).parent / "municipios.json", encoding="utf-8") as f:
        _cidades = loads(f.read())
    return _cidades


def validar_codigo_cidade(codigo: int) -> bool:
    cidades = ler_cidades()
    return any(cidade["id"] == codigo for cidade in cidades)


def normalizar_uf(uf: str) -> str:
    cidades = ler_cidades()
    uf = uf.upper()
    assert any(
        cidade["regiao-imediata"]["regiao-intermediaria"]["UF"]["sigla"] == uf
        for cidade in cidades
    ), "UF não encontrada. Insira uma UF válida no formato de sigla (ex: SP, RJ, MG, etc)"
    return uf


class UF(Enum):
    ACRE = "AC"
    ALAGOAS = "AL"
    AMAPA = "AP"
    AMAZONAS = "AM"
    BAHIA = "BA"
    CEARA = "CE"
    DISTRITO_FEDERAL = "DF"
    ESPIRITO_SANTO = "ES"
    GOIAS = "GO"
    MARANHAO = "MA"
    MATO_GROSSO = "MT"
    MATO_GROSSO_DO_SUL = "MS"
    MINAS_GERAIS = "MG"
    PARA = "PA"
    PARAIBA = "PB"
    PARANA = "PR"
    PERNAMBUCO = "PE"
    PIAUI = "PI"
    RIO_DE_JANEIRO = "RJ"
    RIO_GRANDE_DO_NORTE = "RN"
    RIO_GRANDE_DO_SUL = "RS"
    RONDONIA = "RO"
    RORAIMA = "RR"
    SANTA_CATARINA = "SC"
    SAO_PAULO = "SP"
    SERGIPE = "SE"
    TOCANTINS = "TO"
