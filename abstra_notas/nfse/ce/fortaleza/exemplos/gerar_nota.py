from abstra_notas.nfse.ce.fortaleza import EnvioRPS, Cliente
from abstra_notas.validacoes.cidades import UF
from datetime import date
from dotenv import load_dotenv
from os import getenv
from pathlib import Path

load_dotenv()

cliente = Cliente(
    caminho_pfx=Path(getenv("NFSE_PFX_PATH")), 
    senha_pfx=getenv("NFSE_PFX_PASSWORD")
)

pedido = EnvioRPS(
    remetente=getenv("NFSE_CNPJ_REMETENTE"),
    inscricao_prestador=getenv("NFSE_INSCRICAO_PRESTADOR"),
    numero_rps=1,
    serie_rps="TESTE",
    data_emissao=date(2023, 1, 1),
    discriminacao="Desenvolvimento de sistema web",
    codigo_servico="1.01",
    aliquota_servicos=0.05,
    valor_servicos_centavos=10000,  # R$ 100,00
    valor_deducoes_centavos=0,
    tomador_cnpj_cpf=getenv("NFSE_CNPJ_TOMADOR"),
    tomador_razao_social="Nome do Tomador",
    tomador_endereco_logradouro="Rua das Flores",
    tomador_endereco_numero="123",
    tomador_endereco_bairro="Centro",
    tomador_endereco_cidade=2304400,  # Fortaleza
    tomador_endereco_uf=UF.CE,
    tomador_endereco_cep="60000-000",
    tomador_email="tomador@exemplo.com",
)

try:
    resultado = cliente.gerar_nota(pedido)
    print("Nota gerada com sucesso!")
    print(f"Número da NFSe: {resultado.numero_nfse}")
    print(f"Código de verificação: {resultado.codigo_verificacao}")
except Exception as e:
    print(f"Erro ao gerar nota: {e}")
