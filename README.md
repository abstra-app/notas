# Abstra Notas

Biblioteca de emissão de notas fiscais eletrônicas para empresas brasileiras.


Se você está interessado em automações financeiras com Python, dê uma olhada na [Abstra](https://abstra.io/).

## Instalação

```bash
pip install abstra_notas
```

## Exemplos

```python
from abstra_notas.nfse.sp.sao_paulo import (
    PedidoConsultaCNPJ,
    Cliente,
    RetornoConsultaCNPJ,
)

cliente = Cliente(caminho_pfx="/meu/caminho/certificado.pfx", senha_pfx="senha")

pedido = PedidoConsultaCNPJ(
    remetente="54.188.924/0001-92",
    destinatario="131.274.830-31",
)

retorno = cliente.consultar_cnpj(pedido)

print(retorno.sucesso)
```

```python
from abstra_notas.nfse.sp.sao_paulo import PedidoEnvioRPS, Cliente, RetornoEnvioRPS
from datetime import date


cliente = Cliente(
    caminho_pfx="/meu/caminho/certificado.pfx",
    senha_pfx="senha"
)

pedido = PedidoEnvioRPS(
    remetente="54.188.924/0001-92",
    tomador="131.274.830-31",
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
    valor_servicos_centavos=10000
)

retorno = cliente.gerar_nota(pedido)

print(retorno.sucesso)
```

## Licença

MIT
