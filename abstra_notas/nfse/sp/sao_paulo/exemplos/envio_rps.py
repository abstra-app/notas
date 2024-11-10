from abstra_notas.nfse.sp.sao_paulo import EnvioRPS, Cliente, ErroEnvioRps
from datetime import date
from dotenv import load_dotenv
from os import getenv
from pathlib import Path

load_dotenv()


cliente = Cliente(
    caminho_pfx=Path(getenv("NFSE_PFX_PATH")), senha_pfx=getenv("NFSE_PFX_PASSWORD")
)

pedido = EnvioRPS(
    remetente=getenv("NFSE_CNPJ_REMETENTE"),
    tomador=getenv("NFSE_CNPJ_TOMADOR"),
    aliquota_servicos=0.01,
    codigo_servico=1,
    data_emissao=date(2021, 1, 1),
    endereco_bairro="Bairro",
    discriminacao="Descrição",
    email_tomador="email@tomador.com",
    endereco_cep="00000-000",
    endereco_cidade=3550308,
    endereco_complemento="Complemento",
    endereco_logradouro="Logradouro",
    endereco_numero="Número",
    endereco_tipo_logradouro="Rua",
    endereco_uf="SP",
    inscricao_prestador=getenv("NFSE_INSCRICAO_PRESTADOR"),
    iss_retido=False,
    numero_rps=1,
    razao_social_tomador="Razão Social",
    serie_rps="1",
    status_rps="N",
    tipo_rps="RPS",
    tributacao_rps="T",
    valor_cofins_centavos=0,
    valor_csll_centavos=0,
    valor_deducoes_centavos=0,
    valor_inss_centavos=0,
    valor_ir_centavos=0,
    valor_pis_centavos=0,
    valor_servicos_centavos=10000,
)


try:
    retorno = cliente.gerar_nota(pedido)
    print(retorno)
except ErroEnvioRps as e:
    print(f"Código: {e.codigo}")
    print(f"Descrição: {e.descricao}")
