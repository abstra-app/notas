import sys
from os.path import curdir
from dotenv import load_dotenv

load_dotenv()

sys.path.append(curdir)

from abstra_notas.nfse.sp.sao_paulo.metodos import consultar_cnpj


print(consultar_cnpj("17.289.475/0001-42"))
