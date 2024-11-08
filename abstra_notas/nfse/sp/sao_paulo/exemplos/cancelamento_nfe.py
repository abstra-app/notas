from abstra_notas.nfse.sp.sao_paulo import (
    CancelamentoNFe,
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

retorno = pedido.executar(cliente)

if retorno.sucesso:
    print("Cancelamento realizado com sucesso")
    print(retorno)
else:
    print("Erro ao cancelar")
    print(retorno)
