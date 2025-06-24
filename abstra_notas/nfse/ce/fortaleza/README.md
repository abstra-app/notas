# Emissão de notas fiscais para a cidade de Fortaleza

Biblioteca de emissão de notas fiscais eletrônicas para empresas da cidade de Fortaleza, Ceará.

A integração é feita através do webservice oficial da Prefeitura de Fortaleza utilizando o padrão ABRASF.

[Abstra Notas](/README.md) > [NFSe](/abstra_notas/nfse/README.md) > [CE](/abstra_notas/nfse/ce/README.md) > Fortaleza

## Funcionalidades Implementadas

- [x] [Gerar nota](/abstra_notas/nfse/ce/fortaleza/exemplos/gerar_nota.py)
- [x] [Gerar notas em lote](/abstra_notas/nfse/ce/fortaleza/exemplos/gerar_notas_em_lote.py)
- [x] [Cancelar nota](/abstra_notas/nfse/ce/fortaleza/exemplos/cancelamento_nfe.py)
- [x] [Consultar CNPJ](/abstra_notas/nfse/ce/fortaleza/exemplos/consulta_cnpj.py)
- [x] [Consultar nota emitida (por RPS)](/abstra_notas/nfse/ce/fortaleza/exemplos/consultar_nota.py)
- [x] Consultar notas emitidas (por período)

## Configuração

Para utilizar a biblioteca, você precisa:

1. **Certificado Digital A1**: Arquivo .pfx com o certificado digital da empresa
2. **Inscrição Municipal**: Número da inscrição municipal em Fortaleza
3. **CNPJ/CPF**: Documento da empresa prestadora de serviços

## Exemplo de Uso

```python
from abstra_notas.nfse.ce.fortaleza import EnvioRPS, Cliente
from abstra_notas.validacoes.cidades import UF
from datetime import date
from pathlib import Path

# Configurar o cliente
cliente = Cliente(
    caminho_pfx=Path("certificado.pfx"), 
    senha_pfx="senha_do_certificado"
)

# Criar o RPS
pedido = EnvioRPS(
    remetente="12.345.678/0001-90",
    inscricao_prestador="12345678",
    numero_rps=1,
    serie_rps="TESTE",
    data_emissao=date(2023, 1, 1),
    discriminacao="Desenvolvimento de sistema web",
    codigo_servico="1.01",
    aliquota_servicos=0.05,
    valor_servicos_centavos=10000,  # R$ 100,00
    tomador_cnpj_cpf="987.654.321-00",
    tomador_razao_social="Nome do Tomador",
    tomador_email="tomador@exemplo.com",
)

# Enviar para a prefeitura
resultado = cliente.gerar_nota(pedido)
print(f"NFSe gerada: {resultado.numero_nfse}")
```

## Códigos de Serviço

Fortaleza utiliza a lista de serviços conforme a legislação municipal. Consulte a lista oficial de códigos de serviço no site da Prefeitura de Fortaleza.

## Ambiente de Testes

Fortaleza disponibiliza um ambiente de homologação para testes. Para utilizar:

1. Configure a URL do webservice para o ambiente de homologação
2. Utilize certificados de teste fornecidos pela prefeitura
3. Os dados gerados no ambiente de homologação não têm validade fiscal

## Observações Importantes

- Todas as datas devem estar no formato YYYY-MM-DD
- Valores monetários são informados em centavos (ex: R$ 100,00 = 10000)
- O código do município de Fortaleza é 2304400
- A inscrição municipal deve ter 8 dígitos
- O tomador é opcional, mas recomendado para emissão completa da NFSe

## Suporte

Para dúvidas sobre a integração com a Prefeitura de Fortaleza, consulte:
- Documentação oficial da NFSe de Fortaleza
- Portal do contribuinte: https://www.fortaleza.ce.gov.br/
