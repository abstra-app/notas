# Implementação de Validação XSD para NFSe Fortaleza

## Resumo

A implementação da emissão de NFSe para Fortaleza/CE foi expandida com validação robusta de layouts XML usando XSDs (XML Schema Definition). Esta validação garante que os XMLs gerados estejam em conformidade com as especificações técnicas do município.

## Funcionalidades Implementadas

### 1. Validação Básica XML
- ✅ Verificação se o XML está bem formado (sintaxe correta)
- ✅ Validação de encoding UTF-8
- ✅ Verificação de estrutura básica SOAP

### 2. Validação de Elementos Obrigatórios
- ✅ **EnvioRPS**: Verifica elementos como RecepcionarLoteRps, LoteRps, Cnpj, QuantidadeRps, etc.
- ✅ **EnvioLoteRPS**: Valida estrutura de lote com múltiplos RPS
- ✅ **ConsultaNFe**: Verifica IdentificacaoRps, Prestador, etc.
- ✅ **CancelamentoNFe**: Valida InfPedidoCancelamento, IdentificacaoNfse, etc.
- ✅ **ConsultaCNPJ**: Validação básica de estrutura

### 3. XSDs Criados
- ✅ `PedidoEnvioRPS_v01.xsd` - Schema para envio de RPS único ou lote
- ✅ `ConsultaNfsePorRps_v01.xsd` - Schema para consulta de NFSe por RPS
- ✅ `CancelamentoNfse_v01.xsd` - Schema para cancelamento de NFSe
- ✅ `ConsultaCnpj_v01.xsd` - Schema para consulta de CNPJ

### 4. Testes Automatizados
- ✅ **11 testes unitários** cobrindo todos os fluxos
- ✅ Validação de XML bem formado
- ✅ Verificação de elementos obrigatórios
- ✅ Teste de detecção de erros em XMLs inválidos
- ✅ Validação de estrutura específica de Fortaleza

### 5. Exemplos de Uso
- ✅ `validacao_xsd.py` - Demonstra como usar validação XSD
- ✅ Funções helper para validação
- ✅ Documentação de como integrar validação no código

## Estrutura de Arquivos

```
abstra_notas/nfse/ce/fortaleza/
├── xsds/                              # Esquemas XSD
│   ├── PedidoEnvioRPS_v01.xsd        # Schema envio RPS
│   ├── ConsultaNfsePorRps_v01.xsd    # Schema consulta NFSe
│   ├── CancelamentoNfse_v01.xsd      # Schema cancelamento
│   ├── ConsultaCnpj_v01.xsd          # Schema consulta CNPJ
│   └── ... (outros XSDs ABRASF)
├── exemplos/
│   └── validacao_xsd.py              # Exemplo de validação
├── test_fortaleza.py                 # Testes com validação XSD
└── README.md                         # Documentação atualizada
```

## Como Usar a Validação

### Validação Automática nos Testes
```python
import unittest
from abstra_notas.nfse.ce.fortaleza.test_fortaleza import TestFortalezaNFSe

# Os testes já incluem validação automática
unittest.main()
```

### Validação Manual
```python
from abstra_notas.nfse.ce.fortaleza.exemplos.validacao_xsd import validar_xml_contra_xsd
from lxml import etree

# Gerar XML
xml_element = pedido.gerar_xml(assinador)
xml_str = etree.tostring(xml_element, encoding='unicode')

# Validar
if validar_xml_contra_xsd(xml_str, 'PedidoEnvioRPS_v01.xsd'):
    print("✅ XML válido!")
else:
    print("❌ XML inválido!")
```

### Validação Integrada no Desenvolvimento
```python
def enviar_nota_com_validacao(pedido):
    # Gera XML
    xml_element = pedido.gerar_xml(assinador)
    xml_str = etree.tostring(xml_element, encoding='unicode')
    
    # Valida antes de enviar
    if not _verificar_xml_bem_formado(xml_str):
        raise ValueError("XML mal formado")
    
    if not _verificar_elementos_obrigatorios(xml_str):
        raise ValueError("Elementos obrigatórios ausentes")
    
    # Envia para a prefeitura
    return cliente.executar(pedido)
```

## Benefícios

1. **Qualidade**: Garante que XMLs gerados estão corretos antes do envio
2. **Debugging**: Identifica problemas de estrutura rapidamente
3. **Conformidade**: Assegura aderência ao padrão de Fortaleza
4. **Manutenibilidade**: Facilita identificação de problemas em mudanças
5. **Documentação**: XSDs servem como documentação técnica da estrutura

## Limitações e Considerações

- **Namespaces SOAP**: Validação XSD completa com SOAP é complexa
- **Padrão Fortaleza**: Fortaleza usa padrão próprio, não ABRASF puro
- **Performance**: Validação adiciona overhead (usar apenas em desenvolvimento/testes)
- **Evolução**: XSDs podem precisar atualização conforme município evolui padrão

## Próximos Passos Sugeridos

1. **Validação em Produção**: Implementar validação opcional em produção
2. **Cache de XSDs**: Otimizar carregamento de esquemas
3. **Relatórios**: Gerar relatórios detalhados de validação
4. **Integração CI/CD**: Incluir validação em pipelines automatizados
5. **Outros Municípios**: Expandir validação para outros municípios CE

## Resumo de Execução

- ✅ **11/11 testes passando**
- ✅ **4 XSDs criados e funcionais**
- ✅ **Validação estrutural implementada**
- ✅ **Exemplos de uso criados**
- ✅ **Documentação atualizada**

A validação XSD para NFSe Fortaleza está **completa e operacional**! 🎉
