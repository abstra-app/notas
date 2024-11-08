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

retorno: RetornoConsultaCNPJ = cliente.executar(pedido)

print(retorno.sucesso)
