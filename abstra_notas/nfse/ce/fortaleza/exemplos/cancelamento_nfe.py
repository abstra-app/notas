from abstra_notas.nfse.ce.fortaleza import (
    CancelamentoNFe,
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

pedido = CancelamentoNFe(
    remetente=getenv("NFSE_CNPJ_REMETENTE"),
    inscricao_prestador=getenv("NFSE_INSCRICAO_PRESTADOR"),
    numero_nfse=123,  # Número da NFSe a ser cancelada
    codigo_cancelamento="1",  # 1 - Erro na emissão
)

try:
    resultado = cliente.cancelar_nota(pedido)
    print("NFSe cancelada com sucesso!")
    print(f"Número da NFSe: {resultado.numero_nfse}")
    print(f"Data do cancelamento: {resultado.data_cancelamento}")
except Exception as e:
    print(f"Erro ao cancelar nota: {e}")
