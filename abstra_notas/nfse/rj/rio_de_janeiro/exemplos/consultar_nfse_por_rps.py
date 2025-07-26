from abstra_notas.nfse.rj.rio_de_janeiro import ConsultarNfsePorRpsEnvio, TipoRps, IdentificacaoRps
from dotenv import load_dotenv
from os import getenv
from pathlib import Path

load_dotenv()

# Configuração das credenciais
caminho_certificado = Path(getenv("NFSE_PFX_PATH", "certificado.pfx"))
senha_certificado = getenv("NFSE_PFX_PASSWORD", "senha_certificado")

# Dados do prestador
prestador_cnpj = getenv("NFSE_CNPJ_PRESTADOR", "12345678000123")
prestador_inscricao = getenv("NFSE_INSCRICAO_PRESTADOR", "123456")

# Dados do RPS a consultar
rps_numero = "1"
rps_serie = "1"

# Criar o pedido de consulta
consulta = ConsultarNfsePorRpsEnvio(
    prestador_cnpj=prestador_cnpj,
    prestador_inscricao_municipal=prestador_inscricao,
    identificacao_rps=IdentificacaoRps(
        numero=rps_numero,
        serie=rps_serie,
        tipo=TipoRps.rps
    )
)

try:
    # Executar a consulta
    resposta = consulta.executar(
        caminho_pfx=caminho_certificado,
        senha_pfx=senha_certificado
    )
    
    print(f"Resposta da consulta NFSe por RPS: {resposta}")
    print(f" Consulta realizada para RPS: {rps_numero}/{rps_serie}")
    
    if resposta.comp_nfse:
        nfse = resposta.comp_nfse.nfse
        print(f"\n NFSe encontrada:")
        print(f"    Número: {nfse.numero}")
        print(f"    Data de emissão: {nfse.data_emissao}")
        print(f"    Valor do serviço: R$ {nfse.servico.valores.valor_servico_centavos / 100:.2f}")
        print(f"    Código de verificação: {nfse.codigo_verificacao}")
        
        if resposta.comp_nfse.nfse_cancelamento:
            print(f"   Status: CANCELADA em {resposta.comp_nfse.nfse_cancelamento.data_hora_cancelamento}")
        else:
            print(f"   Status: ATIVA")
        
        # Informações do RPS original
        rps_info = resposta.comp_nfse.nfse.identificacao_rps
        print(f"\n RPS Original:")
        print(f"   Número: {rps_info.numero}")
        print(f"   Série: {rps_info.serie}")
        print(f"   Tipo: {rps_info.tipo.value}")
        
        # Informações do serviço
        if hasattr(nfse, 'servico'):
            print(f"\n  Serviço:")
            print(f"   Discriminação: {nfse.servico.discriminacao}")
            print(f"   Código do município: {nfse.servico.codigo_municipio}")
            print(f"   Valor ISS: R$ {nfse.servico.valores.valor_iss_centavos / 100:.2f}")
            print(f"   Alíquota ISS: {nfse.servico.valores.aliquota_iss}%")
    else:
        print("NFSe não encontrada para este RPS")
    
    if resposta.lista_mensagem_retorno:
        print("\n📋 Mensagens de retorno:")
        for msg in resposta.lista_mensagem_retorno:
            print(f"{msg.codigo}: {msg.mensagem}")
            
except Exception as e:
    print(f"Erro ao consultar NFSe por RPS: {str(e)}")