from abstra_notas.nfse.sp.sao_paulo import (
    CancelamentoNFe,
    Cliente,
)

cliente = Cliente(caminho_pfx="roberto.pfx", senha_pfx="Vera1508")

pedido = CancelamentoNFe(
    inscricao_prestador="74122711",
    numero_nfe=79,
    remetente="47380832000144",
    transacao="true",
)

retorno = pedido.executar(cliente)

if retorno.sucesso:
    print("Cancelamento realizado com sucesso")
    print(retorno)
else:
    print("Erro ao cancelar")
    print(retorno)
