from os import getenv
from pathlib import Path
from dotenv import load_dotenv
from abstra_notas.nfse.rj.rio_de_janeiro import CancelarNfseEnvio, PedidoCancelamento, IdentificacaoNfse

load_dotenv()

numero_nfse="1"

caminho_certificado = Path(getenv("NFSE_PFX_PATH", "certificado.pfx"))
senha_certificado = getenv("NFSE_PFX_PASSWORD", "senha_certificado")

# Dados do prestador
prestador_cnpj = getenv("NFSE_CNPJ_PRESTADOR", "12345678000123")
prestador_inscricao = getenv("NFSE_INSCRICAO_PRESTADOR", "1234567")

cancelamento = CancelarNfseEnvio(
    PedidoCancelamento(
        id=f"NF{numero_nfse}",
        identificacao_nfse=IdentificacaoNfse(
            numero=numero_nfse,
            cnpj=prestador_cnpj,
            inscricao_municipal=prestador_inscricao,
            codigo_municipio=3304557  # Código de Rio de Janeiro
        )
    )
)

try:
    # Executar o cancelamento
    resposta = cancelamento.executar(
        caminho_pfx=caminho_certificado,
        senha_pfx=senha_certificado,
        homologacao=True  # Defina como True para ambiente de homologação
    )
    print(f"Resposta do cancelamento: {resposta}")
    
    
    if resposta.data_hora_cancelamento:
        print(f"Data/Hora: {resposta.data_hora_cancelamento}")
        print(f"Código de cancelamento: {resposta.pedido_cancelamento.codigo_cancelamento}")
    
    # Para cancelamentos bem-sucedidos, verificar se há lista de mensagens
    if hasattr(resposta, 'lista_mensagem_retorno') and resposta.lista_mensagem_retorno:
        print("\nMensagens de retorno:")
        for msg in resposta.lista_mensagem_retorno:
            print(f"{msg.codigo}: {msg.mensagem}")
    
    # Para respostas com mensagem única (como erro)
    elif hasattr(resposta, 'mensagem_retorno') and resposta.mensagem_retorno:
        msg = resposta.mensagem_retorno
        print(f"\nMensagem: {msg.codigo}: {msg.mensagem}")
        if hasattr(msg, 'correcao') and msg.correcao:
            print(f"Correção: {msg.correcao}")
            
except Exception as e:
    print(f"Erro ao cancelar NFSe: {str(e)}")
