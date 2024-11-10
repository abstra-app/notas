# Abstra Notas

Biblioteca de emissão de notas fiscais eletrônicas para empresas brasileiras.


Se você está interessado em automações financeiras com Python, dê uma olhada na [Abstra](https://abstra.io/).

```python
from abstra_notas.nfse.sp.sao_paulo import Cliente


cliente = Cliente(
    caminho_pfx="/meu/caminho/certificado.pfx",
    senha_pfx="senha"
)

...

cliente.gerar_nota(pedido) # Simples assim
```

## Instalação

```bash
pip install abstra_notas
```

## Exemplos

- [NFSe](/abstra_notas/nfse/README.md): Notas de serviço via prefeituras.
- NFe: Notas de produtos via SEFAZ (Em breve)

## Licença

MIT
