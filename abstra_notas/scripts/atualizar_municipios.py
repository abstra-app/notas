from requests import get
from datetime import date

header = "\n".join(
    [
        "'''",
        "Este arquivo foi gerado automaticamente. Ultima atualização: "
        + str(date.today()),
        "Script para atualizar a lista de municípios do IBGE.",
        "Path: abstra_notas/scripts/atualizar_municipios.py",
        "'''",
    ]
)

url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
data = get(url).json()
