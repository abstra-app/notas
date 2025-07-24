from abstra_notas.nfse.ce.fortaleza import ConsultarLoteRpsEnvio
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

# Protocolo do lote a consultar
protocolo = "123456789"

# Criar o pedido de consulta
consulta = ConsultarLoteRpsEnvio(
    prestador_cnpj=prestador_cnpj,
    prestador_inscricao_municipal=prestador_inscricao,
    protocolo=protocolo
)

try:
    # Executar a consulta
    resposta = consulta.executar(
        caminho_pfx=caminho_certificado,
        senha_pfx=senha_certificado
    )
    
    print(f"Consulta realizada para o protocolo: {protocolo}")
    
    if hasattr(resposta, 'comp_nfse') and resposta.comp_nfse:
        print(f"\nEncontradas {len(resposta.comp_nfse)} NFSe(s):")
        for comp_nfse in resposta.comp_nfse:
            nfse = comp_nfse.nfse
            print(f"NFSe: {nfse.numero} | RPS: {nfse.identificacao_rps.numero}/{nfse.identificacao_rps.serie}")
            
            # Verificar se foi cancelada
            if hasattr(comp_nfse, 'cancelamento') and comp_nfse.cancelamento and comp_nfse.cancelamento.sucesso:
                print(f"Status: CANCELADA em {comp_nfse.cancelamento.data_hora}")
            else:
                print(f"Status: ATIVA")
    else:
        print("Nenhuma NFSe encontrada para este lote")
    
    if hasattr(resposta, 'lista_mensagem_retorno') and resposta.lista_mensagem_retorno:
        print("\nMensagens:")
        for msg in resposta.lista_mensagem_retorno:
            print(f"{msg.codigo}: {msg.mensagem}")
            
except Exception as e:
    print(f"Erro: {str(e)}")
