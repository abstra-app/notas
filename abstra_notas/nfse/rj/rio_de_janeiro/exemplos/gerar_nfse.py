from abstra_notas.nfse.rj.rio_de_janeiro import (
    GerarNfseEnvio,
    Rps,
    DadosTomador,
    IdentificacaoRps,
    NaturezaOperacao,
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
    identificacao_rps=IdentificacaoRps(
        numero=1003,
        tipo= TipoRps.rps,
        serie=1
    ),
    data_emissao="2025-07-28T10:00:00",
    natureza_operacao=NaturezaOperacao.tributacao_no_municipio,
    optante_simples_nacional=False,
    incentivador_cultural=False,
    status=StatusRps.normal,
    servico=DadosServico(
        discriminacao="Serviços de desenvolvimento de software",
        codigo_municipio=3304557, 
        valores=Valores(
            valor_servico_centavos=100000,  # R$ 1.000,00
            valor_iss_centavos=5000,       # R$ 50,00 (5%)
            aliquota_iss=0.05,             # 5%
        ),
        codigo_tributacao_municipio="010502",
        item_lista_servico="0105"
    ),
    prestador_cnpj=prestador_cnpj,
    prestador_inscricao_municipal=prestador_inscricao,
    tomador=DadosTomador(
        cnpj=tomador_cnpj,
        razao_social=tomador_razao_social,
        endereco=Endereco(
            logradouro="Rua Visconde de inhaúma",
            numero="112",
            bairro="Centro",
            codigo_municipio=3304557,  # Código de Rio de Janeiro
        uf="RJ",
        cep="20030-001",
        complemento="Complemento do endereço",
    ),
    contato=Contato(
        telefone="21 999999999",
    )),
)

# Criar o envio do lote
envio = GerarNfseEnvio(
    rps=rps
)

try:
    # Executar o envio
    resposta = envio.executar(
        caminho_pfx=caminho_certificado,
        senha_pfx=senha_certificado,
        homologacao=True  # Defina como True para ambiente de homologação
    )
    
    
    # Verificar se o atributo existe antes de acessá-lo
    if hasattr(resposta, 'comp_nfse') and resposta.comp_nfse:
        print(f"NFSe gerada: {resposta.comp_nfse.nfse.numero}")
        print(f"Data de emissão: {resposta.comp_nfse.nfse.data_emissao}")
        print(f"Código de verificação: {resposta.comp_nfse.nfse.codigo_verificacao}")

    if hasattr(resposta, 'lista_mensagem_retorno') and resposta.lista_mensagem_retorno:
        print("\nMensagens de retorno:")
        for msg in resposta.lista_mensagem_retorno:
            print(f"   {msg.codigo}: {msg.mensagem}")
            
except Exception as e:
    print(f"Erro ao enviar lote: {str(e)}")