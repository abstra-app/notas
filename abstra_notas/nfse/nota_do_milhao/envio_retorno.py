from dataclasses import dataclass


@dataclass
class Cabecalho:
    sucesso: bool

@dataclass
class ChaveNFe:
    inscricao_prestador: str
    numero_nfe: int
    codigo_verificacao: str

@dataclass
class ChaveRPS:
    inscricao_prestador: str
    serie_rps: str
    numero_rps: int

@dataclass
class ChaveNFeRPS:
    chave_nfe: ChaveNFe
    chave_rps: ChaveRPS

@dataclass
class RetornoEnvioRPS:
    cabecalho: Cabecalho
    chave_nfe_rps: ChaveNFeRPS