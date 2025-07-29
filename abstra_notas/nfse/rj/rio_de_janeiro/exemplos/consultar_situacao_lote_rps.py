
from os import getenv
from abstra_notas.nfse.rj.rio_de_janeiro import ConsultarSituacaoLoteRpsEnvio
from dotenv import load_dotenv

load_dotenv()


# Dados do prestador
prestador_cnpj = getenv("NFSE_CNPJ_PRESTADOR", "12345678000123")
prestador_inscricao = getenv("NFSE_INSCRICAO_PRESTADOR", "1234567")

protocolo="12312"

# Criar o pedido de consulta
consulta = ConsultarSituacaoLoteRpsEnvio(
    prestador_cnpj=prestador_cnpj,
    protocolo=protocolo
)

try:
    # Executar a consulta
    resposta = consulta.executar(
        caminho_pfx=caminho_certificado,
        senha_pfx=senha_certificado,
        homologacao=True  # Defina como True para ambiente de homologação
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
            print(f"    {msg.codigo}: {msg.mensagem}. Correção: {msg.correcao}")
            
except Exception as e:
    print(f" Erro ao consultar situação do lote: {str(e)}")