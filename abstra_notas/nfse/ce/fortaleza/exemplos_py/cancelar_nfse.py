from abstra_notas.nfse.ce.fortaleza import CancelarNfseEnvio
from pathlib import Path
from dotenv import load_dotenv
from os import getenv

load_dotenv()

# Configuração das credenciais
caminho_certificado = Path(getenv("NFSE_PFX_PATH", "certificado.pfx"))
senha_certificado = getenv("NFSE_PFX_PASSWORD", "senha_certificado")

# Dados do prestador
prestador_cnpj = getenv("NFSE_CNPJ_PRESTADOR", "12345678000123")
prestador_inscricao = getenv("NFSE_INSCRICAO_PRESTADOR", "123456")

# Número da NFSe a ser cancelada
numero_nfse = "1"

# Criar o pedido de cancelamento
cancelamento = CancelarNfseEnvio(
    prestador_cnpj=prestador_cnpj,
    prestador_inscricao_municipal=prestador_inscricao,
    numero_nfse=numero_nfse,
)

try:
    # Executar o cancelamento
    resposta = cancelamento.executar(
        caminho_pfx=caminho_certificado,
        senha_pfx=senha_certificado
    )
    print(f"Resposta do cancelamento: {resposta}")
    
    print("Cancelamento processado!")
    print(f"Sucesso: {resposta.sucesso}")
    
    if resposta.data_hora:
        print(f"Data/Hora: {resposta.data_hora}")
    
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
            
    # Verificar o status do cancelamento
    if not resposta.sucesso:
        print("\n O cancelamento não foi realizado com sucesso.")
        
except Exception as e:
    print(f"Erro ao cancelar NFSe: {str(e)}")