# NFSe Rio de Janeiro

Implementação para emissão e consulta de Notas Fiscais de Serviços Eletrônicas (NFSe) do município do Rio de Janeiro.

## Estrutura

Esta implementação segue o mesmo padrão da implementação de São Paulo, fornecendo as seguintes funcionalidades:

### Classes Principais

- **Cliente**: Cliente para comunicação com o webservice
- **ClienteMock**: Cliente mock para testes
- **EnvioRPS**: Envio de RPS individual
- **EnvioLoteRPS**: Envio de lote de RPS
- **ConsultaCNPJ**: Consulta de CNPJ/CPF
- **ConsultaNFe**: Consulta de NFe específica
- **ConsultaNFePeriodo**: Consulta de NFe por período
- **CancelamentoNFe**: Cancelamento de NFe

### Classes de Retorno

- **RetornoEnvioRps**: Retorno do envio de RPS
- **RetornoEnvioRpsLote**: Retorno do envio de lote
- **RetornoConsultaCNPJ**: Retorno da consulta de CNPJ
- **RetornoConsulta**: Retorno das consultas de NFe
- **RetornoCancelamentoNFe**: Retorno do cancelamento

### Classes de Suporte

- **RPS**: Recibo Provisório de Serviços
- **Erro**: Classe base para erros
- **Remessa**: Dados do remetente
- **Pedido**: Classe base para pedidos

## Uso

```python
from abstra_notas.nfse.rj.rio_de_janeiro import Cliente, EnvioRPS, RPS
from pathlib import Path
from datetime import date

# Inicializar cliente
cliente = Cliente(Path("certificado.pfx"), "senha")

# Criar RPS
rps = EnvioRPS(
    remetente="12345678000195",
    inscricao_prestador=12345678,
    numero_rps=1,
    tipo_rps="RPS",
    data_emissao=date.today(),
    discriminacao="Serviços de consultoria",
    status_rps="N",
    tributacao_rps="T",
    codigo_servico="0101",
    aliquota_servicos=0.05,
    iss_retido=False,
    valor_servicos_centavos=100000,  # R$ 1.000,00
    valor_deducoes_centavos=0,
    serie_rps="A1",
)

# Enviar RPS
retorno = cliente.gerar_nota(rps)
```

## Observações

- Esta implementação é baseada na estrutura de São Paulo e pode precisar de ajustes específicos para atender às particularidades do webservice do Rio de Janeiro
- As URLs e namespaces XML devem ser verificados conforme a documentação oficial da Prefeitura do Rio de Janeiro
- Os templates XML podem precisar de ajustes conforme os XSDs oficiais do município
