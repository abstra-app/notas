from abstra_notas.nfse.sp.sao_paulo.envio_rps import RPS
import pytest

def test_ler_rps_txt_com_cidade():
    # Constructing a valid line with known positions
    # 1: 1-1
    # Inscricao: 4-12 (8)
    header = "1000000001332025120220251203"
    
    # RPS Line Construction
    # Type 6 (1 char)
    line = "6"
    # Tipo RPS (5 chars)
    line += "RPS  "
    # Serie (5 chars)
    line += "Ak   "
    # Numero RPS (12 chars)
    line += "000000379950"
    # Data Emissao (8 chars)
    line += "20251203"
    # Situacao (1 char)
    line += "T"
    # Valor Servicos (15 chars)
    line += "000000000080150"
    # Valor Deducoes (15 chars)
    line += "000000000000000"
    # Codigo Servico (5 chars)
    line += "02800"
    # Aliquota (4 chars)
    line += "0290"
    # ISS Retido (1 char)
    line += "2"
    # Tipo Tomador (1 char)
    line += "2" # CNPJ
    # CNPJ Tomador (14 chars)
    line += "03010739000172"
    # IM Tomador (8 chars)
    line += "00000000"
    # IE Tomador (12 chars)
    line += "000000000000"
    # Razao Social (75 chars)
    line += "TOMADOR TESTE LTDA".ljust(75)
    # Tipo Logradouro (3 chars)
    line += "RUA"
    # Logradouro (50 chars)
    line += "TESTE".ljust(50)
    # Numero (10 chars)
    line += "117".ljust(10)
    # Complemento (30 chars)
    line += "".ljust(30)
    # Bairro (30 chars) -> Pos 275
    line += "BAIRRO TESTE".ljust(30)
    # Cidade (50 chars) -> Pos 305
    line += "CIDADE TESTE".ljust(50)
    # UF (2 chars) -> Pos 355
    line += "SP"
    # CEP (8 chars) -> Pos 357
    line += "08010260"
    # Email (75 chars) -> Pos 365
    line += "teste@teste.com".ljust(75)
    # Rest of the line (filler to avoid index errors if any)
    line += "0" * 400 

    raw_txt = f"{header}\n{line}\n90000001000000000080150000000000000000"

    lista_rps = RPS.ler_txt(raw_txt)
    assert len(lista_rps) == 1
    rps = lista_rps[0]
    
    assert rps.endereco_bairro == "BAIRRO TESTE"
    assert rps.endereco_cidade == "CIDADE TESTE"
    assert rps.endereco_uf.value == "SP"
