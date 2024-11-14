from abstra_notas.nfse.sp.sao_paulo import ConsultaCNPJ, Cliente, Erro
from dotenv import load_dotenv
from os import getenv

load_dotenv()


cliente = Cliente(
    caminho_pfx=getenv("NFSE_PFX_PATH"), senha_pfx=getenv("NFSE_PFX_PASSWORD")
)

pedido = ConsultaCNPJ(
    remetente=getenv("NFSE_CNPJ_REMETENTE"),
    contribuinte=getenv("NFSE_CNPJ_CONTRIBUINTE"),
)

retorno = cliente.consultar_cnpj(pedido)

try:
    print(f"Inscrição Municipal: {retorno.inscricao_municipal}")
    print(f"Emite NFe: {retorno.emite_nfe}")
except Erro as e:
    print(f"Código: {e.codigo}")
    print(f"Descrição: {e.descricao}")
