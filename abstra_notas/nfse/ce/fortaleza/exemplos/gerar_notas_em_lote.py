from abstra_notas.nfse.ce.fortaleza import Cliente, EnvioLoteRPS, RPS
from datetime import date
from dotenv import load_dotenv
from os import getenv
from pathlib import Path

load_dotenv()

cliente = Cliente(
    caminho_pfx=Path(getenv("NFSE_PFX_PATH")), 
    senha_pfx=getenv("NFSE_PFX_PASSWORD")
)

pedido = EnvioLoteRPS(
    remetente=getenv("NFSE_CNPJ_REMETENTE"),
    numero_lote="LOTE001",
    lista_rps=[
        RPS(
            inscricao_prestador=getenv("NFSE_INSCRICAO_PRESTADOR"),
            numero_rps=1,
            serie_rps="TESTE",
            data_emissao=date.today(),
            discriminacao="Desenvolvimento de sistema web - Item 1",
            codigo_servico="1.01",
            aliquota_servicos=0.05,
            valor_servicos_centavos=10000,  # R$ 100,00
            tomador_cnpj_cpf=getenv("NFSE_CNPJ_TOMADOR"),
            tomador_razao_social="Nome do Tomador",
            tomador_email="tomador@exemplo.com",
        ),
        RPS(
            inscricao_prestador=getenv("NFSE_INSCRICAO_PRESTADOR"),
            numero_rps=2,
            serie_rps="TESTE",
            data_emissao=date.today(),
            discriminacao="Desenvolvimento de sistema web - Item 2",
            codigo_servico="1.01",
            aliquota_servicos=0.05,
            valor_servicos_centavos=15000,  # R$ 150,00
            tomador_cnpj_cpf=getenv("NFSE_CNPJ_TOMADOR"),
            tomador_razao_social="Nome do Tomador",
            tomador_email="tomador@exemplo.com",
        ),
    ]
)

try:
    resultado = cliente.gerar_notas_em_lote(pedido)
    print("Lote enviado com sucesso!")
    print(f"Número do lote: {resultado.numero_lote}")
    print(f"Protocolo: {resultado.protocolo}")
    print(f"Situação: {resultado.situacao}")
except Exception as e:
    print(f"Erro ao enviar lote: {e}")
