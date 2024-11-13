from abstra_notas.nfse.sp.sao_paulo import Cliente, EnvioLoteRPS, RPS
from abstra_notas.validacoes.tipo_logradouro import TipoLogradouro
from datetime import date, timedelta
from dotenv import load_dotenv
from os import getenv
from pathlib import Path

load_dotenv()

cliente = Cliente(
    caminho_pfx=Path(getenv("NFSE_PFX_PATH")), senha_pfx=getenv("NFSE_PFX_PASSWORD")
)

pedido = EnvioLoteRPS(
    data_fim_periodo_transmitido=date(2030, 1, 1),
    data_inicio_periodo_transmitido=date(2020, 1, 1),
    remetente=getenv("NFSE_CNPJ_REMETENTE"),
    lista_rps=[
        RPS(
            inscricao_prestador=getenv("NFSE_INSCRICAO_PRESTADOR"),
            numero_rps=numero_rps,
            tipo_rps="RPS",
            data_emissao=date.today() + timedelta(days=numero_rps),
            discriminacao=f"Teste de emissão de nota fiscal {numero_rps}",
            status_rps="N",
            tributacao_rps="T",
            codigo_servico=1,
            aliquota_servicos=0.02,
            iss_retido=False,
            valor_servicos_centavos=100_00,
            valor_deducoes_centavos=0,
            serie_rps="teste",
        )
        for numero_rps in range(1, 11)
    ],
    transacao=True,
)

retorno = cliente.gerar_notas_em_lote(pedido)
