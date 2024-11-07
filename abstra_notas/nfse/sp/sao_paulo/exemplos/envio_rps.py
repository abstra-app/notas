from abstra_notas.nfse.sp.sao_paulo import PedidoEnvioRPS, Cliente, RetornoEnvioRPS
from datetime import date


cliente = Cliente(caminho_pfx="/meu/caminho/certificado.pfx", senha_pfx="senha")

pedido = PedidoEnvioRPS(
    remetente=("CNPJ", "54.188.924/0001-92"),
    tomador=("CPF", "131.274.830-31"),
    aliquota_servicos=2.0,
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
    inscricao_prestador="12345678",
    iss_retido="false",
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

retorno: RetornoEnvioRPS = cliente.executar(pedido)

print(retorno.sucesso)
