from abstra_notas.nfse.ce.fortaleza import ConsultarSituacaoLoteRpsEnvio
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
consulta = ConsultarSituacaoLoteRpsEnvio(
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
    print(f"Resposta da consulta: {resposta}")
    
    if resposta.numero_lote:
        print(f"\n Informações do Lote:")
        print(f"   Número do lote: {resposta.numero_lote}")
        print(f"   Situação: {resposta.situacao.name}, código {resposta.situacao.value}")
        
        if resposta.situacao.value == "4":  # Lote processado
            print("   Status: Lote processado com sucesso")
        elif resposta.situacao.value == "3":  # Lote processado com erro
            print("    Status: Lote processado com erro")
        elif resposta.situacao.value == "2":  # Lote em processamento
            print("    Status: Lote em processamento")
        elif resposta.situacao.value == "1":  # Lote recebido
            print("    Status: Lote recebido")
        else:
            print(f"   Status: Situação desconhecida ({resposta.situacao})")
    
    if resposta.lista_mensagem_retorno:
        print("\n Mensagens de retorno:")
        for msg in resposta.lista_mensagem_retorno:
            if msg.codigo == "L000":
                print(f"    {msg.codigo}: {msg.mensagem}")
            elif msg.codigo.startswith("E"):
                print(f"    {msg.codigo}: {msg.mensagem}")
            else:
                print(f"    {msg.codigo}: {msg.mensagem}")
            
except Exception as e:
    print(f" Erro ao consultar situação do lote: {str(e)}")