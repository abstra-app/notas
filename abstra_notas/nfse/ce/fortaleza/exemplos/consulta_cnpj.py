from abstra_notas.nfse.ce.fortaleza import (
    ConsultaCNPJ,
    Cliente,
)
from dotenv import load_dotenv
from os import getenv
from pathlib import Path

load_dotenv()

cliente = Cliente(
    caminho_pfx=Path(getenv("NFSE_PFX_PATH")), 
    senha_pfx=getenv("NFSE_PFX_PASSWORD")
)

pedido = ConsultaCNPJ(
    remetente=getenv("NFSE_CNPJ_REMETENTE"),
    cnpj="12.345.678/0001-90",  # CNPJ a ser consultado
)

try:
    resultado = cliente.consultar_cnpj(pedido)
    print("Dados do CNPJ encontrados:")
    print(f"CNPJ: {resultado.cnpj}")
    print(f"Inscrição Municipal: {resultado.inscricao_municipal}")
    print(f"Razão Social: {resultado.razao_social}")
    print(f"Nome Fantasia: {resultado.nome_fantasia}")
    print(f"Endereço: {resultado.endereco}")
    print(f"Email: {resultado.email}")
except Exception as e:
    print(f"Erro ao consultar CNPJ: {e}")
