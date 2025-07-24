from abstra_notas.nfse.ce.fortaleza import ConsultarNfseEnvio
from pathlib import Path
from dotenv import load_dotenv
from os import getenv
from datetime import date, timedelta

load_dotenv()

# Configuração das credenciais
caminho_certificado = Path(getenv("NFSE_PFX_PATH", "certificado.pfx"))
senha_certificado = getenv("NFSE_PFX_PASSWORD", "senha_certificado")

# Dados do prestador
prestador_cnpj = getenv("NFSE_CNPJ_PRESTADOR", "12345678000123")
prestador_inscricao = getenv("NFSE_INSCRICAO_PRESTADOR", "123456")

numero_nfse=1

# Criar o pedido de consulta
consulta = ConsultarNfseEnvio(
    prestador_cnpj=prestador_cnpj,
    prestador_inscricao_municipal=prestador_inscricao,
    numero_nfse=numero_nfse
)

try:
    # Executar a consulta
    resposta = consulta.executar(
        caminho_pfx=caminho_certificado,
        senha_pfx=senha_certificado
    )

    print(f"Consulta realizada para o período: {data_inicial} a {data_final}")
    
    if resposta.comp_nfse:
        print(f"\nEncontradas {len(resposta.comp_nfse)} NFSe(s):")
        for comp_nfse in resposta.comp_nfse:
            nfse = comp_nfse.nfse
            valor_servico = nfse.servico.valores.valor_servico_centavos / 100
            status = "Cancelada" if comp_nfse.cancelamento and comp_nfse.cancelamento.sucesso else "Ativa"
            
            print(f"   NFSe: {nfse.numero}")
            print(f"      Data de emissão: {nfse.data_emissao.strftime('%d/%m/%Y %H:%M')}")
            print(f"      Valor: R$ {valor_servico:.2f}")
            print(f"      Código de verificação: {nfse.codigo_verificacao}")
            print(f"      Status: {status}")
            print(f"      Discriminação: {nfse.servico.discriminacao}")
            print()
    else:
        print("Nenhuma NFSe encontrada no período consultado")
    
    if resposta.lista_mensagem_retorno:
        print("Mensagens de retorno:")
        for msg in resposta.lista_mensagem_retorno:
            status = "OK" if msg.codigo == "L000" else "Aviso"
            print(f"   {status} {msg.codigo}: {msg.mensagem}")
            
except Exception as e:
    print(f"Erro ao consultar NFSe: {str(e)}")
