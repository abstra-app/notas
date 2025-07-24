from abstra_notas.nfse.ce.fortaleza import (
    EnviarLoteRpsEnvio,
    Rps,
    NaturezaOperacao,
    RegimeEspecialTributacao,
    StatusRps,
    DadosServico,
    Valores,
    Endereco,
    TipoRps,
    Contato
)
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

# Dados do tomador
tomador_cnpj = getenv("NFSE_CNPJ_TOMADOR", "98765432000198")
tomador_razao_social = getenv("NFSE_TOMADOR_RAZAO_SOCIAL", "EMPRESA TOMADORA LTDA")

# Criar RPS
rps = Rps(
    id="R1",
    numero=1,
    tipo=TipoRps.rps,
    serie=1,
    data_emissao="2025-07-24T10:00:00",
    natureza_operacao=NaturezaOperacao.tributacao_no_municipio,
    regime_especial_tributacao=RegimeEspecialTributacao.microempresario_e_empresa_de_pequeno_porte,
    optante_simples_nacional=True,
    incentivador_cultural=False,
    status=StatusRps.normal,
    servico=DadosServico(
        discriminacao="Serviços de desenvolvimento de software",
        codigo_municipio=2304400,  # Código de Fortaleza
        valores=Valores(
            valor_servico_centavos=100000,  # R$ 1.000,00
            valor_iss_centavos=3000,       # R$ 30,00 (3%)
            aliquota_iss=0.03,             # 3%
        ),
        codigo_tributacao_municipio="821130001",
        item_lista_servico="01.01"
    ),
    prestador_cnpj=prestador_cnpj,
    prestador_inscricao_municipal=prestador_inscricao,
    tomador_cnpj=tomador_cnpj,
    tomador_endereco=Endereco(
        logradouro="Rua das Flores",
        numero="123",
        bairro="Centro",
        codigo_municipio=2304400,  # Fortaleza
        uf="CE",
        cep="60000000",
        complemento="Sala 101",
    ),
    tomador_contato=Contato(
        telefone="85 999999999",
        email="contato@empresa.com"
    ),
    tomador_razao_social=tomador_razao_social,
)

# Criar o envio do lote
envio = EnviarLoteRpsEnvio(
    lote_id="L1",
    numero_lote="1",
    prestador_cnpj=prestador_cnpj,
    prestador_inscricao_municipal=prestador_inscricao,
    lista_rps=[rps]
)

try:
    # Executar o envio
    resposta = envio.executar(
        caminho_pfx=caminho_certificado,
        senha_pfx=senha_certificado
    )

    print(f"Resposta do envio: {resposta}")
    
    print("Lote enviado com sucesso!")
    print(f"Protocolo: {resposta.protocolo}")
    print(f"Data/Hora: {resposta.data_recebimento}")
    
    # Verificar se o atributo existe antes de acessá-lo
    if hasattr(resposta, 'lista_nfse') and resposta.lista_nfse:
        for nfse in resposta.lista_nfse:
            print(f"NFSe gerada: {nfse.numero}")
            print(f"Data de emissão: {nfse.data_emissao}")
            print(f"Código de verificação: {nfse.codigo_verificacao}")
    else:
        print("Lote enviado para processamento. Use o protocolo para consultar o status.")
    
    if hasattr(resposta, 'lista_mensagem_retorno') and resposta.lista_mensagem_retorno:
        print("\nMensagens de retorno:")
        for msg in resposta.lista_mensagem_retorno:
            print(f"   {msg.codigo}: {msg.mensagem}")
            
except Exception as e:
    print(f"Erro ao enviar lote: {str(e)}")