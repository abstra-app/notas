from abstra_notas.nfse.ce.fortaleza import (
    ConsultaNFe,
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

pedido = ConsultaNFe(
    remetente=getenv("NFSE_CNPJ_REMETENTE"),
    numero_rps=1,
    serie_rps="TESTE",
    inscricao_prestador=getenv("NFSE_INSCRICAO_PRESTADOR"),
)

try:
    resultado = cliente.consultar_nota(pedido)
    if resultado.lista_nfse:
        for nfse in resultado.lista_nfse:
            print(f"NFSe encontrada: {nfse.numero_nfse}")
            print(f"Código de verificação: {nfse.codigo_verificacao}")
            print(f"Data de emissão: {nfse.data_emissao}")
            print(f"Valor dos serviços: R$ {nfse.valor_servicos:.2f}")
    else:
        print("Nenhuma NFSe encontrada com os critérios informados")
except Exception as e:
    print(f"Erro ao consultar nota: {e}")
