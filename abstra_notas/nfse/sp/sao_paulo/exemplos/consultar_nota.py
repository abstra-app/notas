from abstra_notas.nfse.sp.sao_paulo import (
    ConsultaNFe,
    Cliente,
    Erro,
)
from dotenv import load_dotenv
from os import getenv

load_dotenv()


cliente = Cliente(
    caminho_pfx=getenv("NFSE_PFX_PATH"), senha_pfx=getenv("NFSE_PFX_PASSWORD")
)

pedido = ConsultaNFe(
    chave_nfe_codigo_verificacao="PeLp-43xl",
    chave_rps_serie_rps="TESTE",
    chave_rps_numero_rps=1,
    chave_nfe_inscricao_prestador=getenv("NFSE_INSCRICAO_PRESTADOR"),
    chave_rps_inscricao_prestador=getenv("NFSE_INSCRICAO_PRESTADOR"),
    chave_nfe_numero_nfe=getenv("NFSE_NUMERO_NFE"),
    remetente=getenv("NFSE_CNPJ_REMETENTE"),
)

retorno = cliente.consultar_nota(pedido)

try:
    for nfe in retorno.lista_nfe:
        print(nfe)
except Erro as e:
    print(f"Código: {e.codigo}")
    print(f"Descrição: {e.descricao}")
