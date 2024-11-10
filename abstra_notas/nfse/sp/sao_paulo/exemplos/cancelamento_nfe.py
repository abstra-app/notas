from abstra_notas.nfse.sp.sao_paulo import (
    CancelamentoNFe,
    ErroCancelamentoNFe,
    Cliente,
)
from dotenv import load_dotenv
from os import getenv

load_dotenv()


cliente = Cliente(
    caminho_pfx=getenv("NFSE_PFX_PATH"), senha_pfx=getenv("NFSE_PFX_PASSWORD")
)

pedido = CancelamentoNFe(
    inscricao_prestador=getenv("NFSE_INSCRICAO_PRESTADOR"),
    numero_nfe=int(getenv("NFSE_NUMERO_NFE")),
    remetente=getenv("NFSE_CNPJ_REMETENTE"),
    transacao="true",
)


try:
    retorno = cliente.cancelar_nota(pedido)
except ErroCancelamentoNFe as e:
    print(e.descricao)
