# Emissão de notas fiscais para a cidade de Fortaleza - CE

Biblioteca de emissão de notas fiscais eletrônicas para empresas da cidade de Fortaleza, Ceará.

A integração é feita através do webservice da Prefeitura Municipal de Fortaleza utilizando SOAP com o padrão GINFES.

[Abstra Notas](/README.md) > [NFSe](/abstra_notas/nfse/README.md) > [CE](/abstra_notas/nfse/ce/README.md) > Fortaleza

## Funcionalidades Disponíveis

- [Enviar lote de RPS (gerar notas)](/abstra_notas/nfse/ce/fortaleza/exemplos_py/enviar_lote_rps.py)
- [Cancelar NFSe](/abstra_notas/nfse/ce/fortaleza/exemplos_py/cancelar_nfse.py)
- [Consultar NFSe por período](/abstra_notas/nfse/ce/fortaleza/exemplos_py/consultar_nfse_periodo.py)
- [Consultar NFSe por RPS](/abstra_notas/nfse/ce/fortaleza/exemplos_py/consultar_nfse_por_rps.py)
- [Consultar situação do lote RPS](/abstra_notas/nfse/ce/fortaleza/exemplos_py/consultar_situacao_lote.py)
- [Consultar lote RPS](/abstra_notas/nfse/ce/fortaleza/exemplos_py/consultar_lote_rps.py)

## Configuração

Para utilizar a biblioteca, você precisa de:

1. **Certificado Digital**: Arquivo .pfx válido
2. **Senha do Certificado**: Senha para acessar o certificado
3. **Credenciais da Prefeitura**: CNPJ e Inscrição Municipal

## Ambientes Disponíveis

A biblioteca suporta dois ambientes:

### Ambiente de Produção (Padrão)

- **URL**: `https://iss.fortaleza.ce.gov.br/grpfor-iss/ServiceGinfesImplService?wsdl`
- **Uso**: Para emissão real de notas fiscais
- **Parâmetro**: `homologacao=False` (padrão)

### Ambiente de Homologação

- **URL**: `http://isshomo.sefin.fortaleza.ce.gov.br/grpfor-iss/ServiceGinfesImplService?wsdl`
- **Uso**: Para testes e validação antes da produção
- **Parâmetro**: `homologacao=True`
- **⚠️ Importante**: Antes de usar o ambiente de homologação, você deve ativá-lo no site da Prefeitura de Fortaleza (https://iss.fortaleza.ce.gov.br/grpfor) na seção 'Controle de Acesso'.

## Exemplos Práticos

Confira os [exemplos completos com configuração](/abstra_notas/nfse/ce/fortaleza/exemplos_py/) que incluem:

- Configuração via arquivo .env
- Tratamento de erros
- Documentação detalhada
- Exemplos prontos para uso

## Exemplo de Uso Básico

```python
from abstra_notas.nfse.ce.fortaleza import EnviarLoteRpsEnvio
from pathlib import Path

# Enviar um lote de RPS
envio = EnviarLoteRpsEnvio(
    lote_id="L1",
    numero_lote="1",
    prestador_cnpj="12345678000123",
    prestador_inscricao_municipal="123456",
    lista_rps=[rps]  # Lista de objetos Rps
)

# Ambiente de produção (padrão)
resposta = envio.executar(
    caminho_pfx=Path("certificado.pfx"),
    senha_pfx="senha_do_certificado"
)

# Ambiente de homologação (para testes)
resposta_homolog = envio.executar(
    caminho_pfx=Path("certificado.pfx"),
    senha_pfx="senha_do_certificado",
    homologacao=True
)
```

## Observações

- Todos os métodos utilizam o padrão `.executar()` com certificado digital
- Os valores monetários devem ser informados em centavos
- As datas devem seguir o formato ISO 8601 (AAAA-MM-DDTHH:MM:SS)
- O webservice utiliza autenticação via certificado digital A1

## Funcionalidades Específicas

### Controle de Ambiente

- **Desenvolvimento/Testes**: Use sempre `homologacao=True`
- **Produção**: Use `homologacao=False` ou omita o parâmetro
- **URLs são selecionadas automaticamente** conforme o ambiente escolhido
