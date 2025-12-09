from dataclasses import dataclass
from typing import Literal, List, Optional
from lxml.etree import Element, fromstring, ElementBase
import base64
from dateutil.parser import parse
from abstra_notas.validacoes.email import validar_email
from abstra_notas.validacoes.cidades import validar_codigo_cidade, normalizar_uf, UF
from abstra_notas.validacoes.cpfcnpj import normalizar_cpf_ou_cnpj, cpf_ou_cnpj
from abstra_notas.validacoes.cep import normalizar_cep
from abstra_notas.validacoes.tipo_logradouro import TipoLogradouro
from datetime import date
from .remessa import Remessa
from .pedido import Pedido
from .retorno import Retorno
from .templates import load_template
from abstra_notas.assinatura import Assinador
from .erro import Erro
import re
import re


@dataclass
class ChaveNFeRPS(Retorno):
    chave_nfe_inscricao_prestador: str
    chave_nfe_numero_nfe: int
    chave_nfe_codigo_verificacao: str
    chave_rps_inscricao_prestador: str
    chave_rps_serie_rps: str
    chave_rps_numero_rps: int

    def __post_init__(self):
        if isinstance(self.chave_nfe_inscricao_prestador, int):
            self.chave_nfe_inscricao_prestador = str(self.chave_nfe_inscricao_prestador)

        if isinstance(self.chave_rps_inscricao_prestador, int):
            self.chave_rps_inscricao_prestador = str(self.chave_rps_inscricao_prestador)

    @staticmethod
    def ler_xml(xml: ElementBase) -> "ChaveNFeRPS":
        return ChaveNFeRPS(
            chave_nfe_inscricao_prestador=xml.find(".//ChaveNFe")
            .find(".//InscricaoPrestador")
            .text,
            chave_nfe_codigo_verificacao=xml.find(".//ChaveNFe")
            .find(".//CodigoVerificacao")
            .text,
            chave_nfe_numero_nfe=int(xml.find(".//ChaveNFe").find(".//NumeroNFe").text),
            chave_rps_inscricao_prestador=xml.find(".//ChaveRPS")
            .find(".//InscricaoPrestador")
            .text,
            chave_rps_numero_rps=int(xml.find(".//ChaveRPS").find(".//NumeroRPS").text),
            chave_rps_serie_rps=xml.find(".//ChaveRPS").find(".//SerieRPS").text,
        )


@dataclass
class RetornoEnvioRps(ChaveNFeRPS):
    @staticmethod
    def ler_xml(xml: ElementBase) -> "RetornoEnvioRps":
        sucesso = xml.find(".//Sucesso").text
        if sucesso == "false":
            raise ErroEnvioRps(
                codigo=xml.find(".//Codigo").text,
                descricao=xml.find(".//Descricao").text,
            )
        elif sucesso == "true":
            chave = ChaveNFeRPS.ler_xml(xml)
            return RetornoEnvioRps(**chave.__dict__)


@dataclass
class ErroEnvioRps(Erro):
    codigo: int
    descricao: str


@dataclass
class RPS:
    inscricao_prestador: int
    """
    Inscrição Municipal do Prestador.
    """

    numero_rps: int
    """
    Número que identifica o RPS. Deve ser único para cada série de RPS.
    Recomenda-se que seja sequencial, iniciando em 1.
    Use algum banco de dados para salvar o número do RPS e garantir que seja único.
    """

    tipo_rps: Literal["RPS", "RPS-M", "RPS-C"]
    """
    RPS: Recibo Provisório de Serviços.
    
    RPS-M: Recibo Provisório de Serviços proveniente de Nota Fiscal Conjugada (Mista).
    
    RPS-C: Recibo Provisório de Serviços proveniente de Nota Fiscal Conjugada (Comum).
    """

    data_emissao: date
    discriminacao: str
    status_rps: Literal["N", "C"]
    tributacao_rps: Literal["T", "F", "A", "B", "D", "M", "N", "R", "S", "X", "V", "P"]
    """
    T: Tributado em São Paulo

    F: Tributado Fora de São Paulo
    
    A: Tributado em São Paulo, porém Isento
    
    B: Tributado Fora de São Paulo, porém Isento
    
    D: Tributado em São Paulo com isenção parcial
    
    M: Tributado em São Paulo, porém com indicação de imunidade subjetiva
    
    N: Tributado Fora de São Paulo, porém com indicação de imunidade subjetiva
    
    R: Tributado em São Paulo, porém com indicação de imunidade objetiva
    
    S: Tributado fora de São Paulo, porém com indicação de imunidade objetiva
    
    X: Tributado em São Paulo, porém Exigibilidade Suspensa
    
    V: Tributado Fora de São Paulo, porém Exigibilidade Suspensa
    
    P: Exportação de Serviços
    """

    codigo_servico: str
    """
    Informe o código do serviço do RPS. Este código deve pertencer à lista de serviços.

    Código de serviço com 4 ou 5 dígitos.
    """

    aliquota_servicos: float
    """
    Valor percentual da alíquota de serviços entre 0 e 1.
    """
    iss_retido: bool

    valor_servicos_centavos: int
    valor_deducoes_centavos: int

    serie_rps: str
    """
    Série do RPS com 5 posições (caracteres). Completar com espaços em branco à direita caso seja necessário.

    Atenção: Não utilize espaços à esquerda. O conteúdo deverá estar alinhado à esquerda. 
    """

    valor_pis_centavos: Optional[int] = None
    valor_cofins_centavos: Optional[int] = None
    valor_inss_centavos: Optional[int] = None
    valor_ir_centavos: Optional[int] = None
    valor_csll_centavos: Optional[int] = None
    valor_carga_tributaria_centavos: Optional[int] = None
    valor_total_recebido_centavos: Optional[int] = None

    tomador: Optional[str] = None
    """
    CPF ou CNPJ do tomador. Qualquer formato é aceito, ex: 00000000000, 00.000.000/0000-00.
    """
    inscricao_municipal_tomador: Optional[str] = None
    """
    Este elemento só deverá ser preenchido para tomadores no município de São Paulo (CCM).
    
    CCM: Cadastro de Contribuintes Mobiliários.
    """

    inscricao_estadual_tomador: Optional[str] = None

    razao_social_tomador: Optional[str] = None

    email_tomador: Optional[str] = None

    endereco_tipo_logradouro: Optional[TipoLogradouro] = None
    endereco_logradouro: Optional[str] = None
    endereco_numero: Optional[str] = None
    endereco_complemento: Optional[str] = None
    endereco_uf: Optional[UF] = None
    endereco_cidade: Optional[str] = None
    """
    Código da cidade. Pode ser obtido em:

    https://servicodados.ibge.gov.br/api/v1/localidades/municipios
    """
    endereco_bairro: Optional[str] = None
    endereco_cep: Optional[str] = None

    intermediario: Optional[str] = None
    """
    CPF ou CNPJ do intermediário. Qualquer formato é aceito, ex: 00000000000, 00.000.000/0000-00.
    """

    inscricao_municipal_intermediario: Optional[str] = None
    """
    Este elemento só deverá ser preenchido para intermediários no município de São Paulo (CCM).
    """

    iss_retido_intermediario: Optional[bool] = None
    email_intermediario: Optional[str] = None

    percentual_carga_tributaria: Optional[float] = None
    """
    Valor percentual da carga tributária entre 0 e 1.
    """

    fonte_carga_tributaria: Optional[str] = None
    """
    Fonte da carga tributária. Máximo de 10 caracteres.
    """

    codigo_cei: Optional[int] = None
    """
    Cadastro Específico do INSS.
    """

    matricula_obra: Optional[int] = None
    """
    Número de matrícula de obra.
    """

    municipio_prestacao: Optional[int] = None
    """
    Código do município onde o serviço foi prestado.

    Codigo do municipio pode ser obtido em:

    https://servicodados.ibge.gov.br/api/v1/localidades/municipios
    """

    numero_encapsulamento: Optional[int] = None
    """
    Código de encapsulamento de notas dedutoras.
    """

    def __post_init__(self):
        if isinstance(self.data_emissao, str):
            self.data_emissao = parse(self.data_emissao).date()

        if self.endereco_cep is not None:
            self.endereco_cep = normalizar_cep(self.endereco_cep)

        assert (
            self.endereco_bairro is None or len(self.endereco_bairro) <= 30
        ), "O bairro deve ter no máximo 30 caracteres"

        if self.endereco_uf is not None:
            if isinstance(self.endereco_uf, str):
                uf_str = self.endereco_uf
            else:
                uf_str = self.endereco_uf.value
            self.endereco_uf = UF(normalizar_uf(uf_str))

        if self.tomador is not None:
            self.tomador = normalizar_cpf_ou_cnpj(self.tomador)

        if self.endereco_cidade is not None:
            if str(self.endereco_cidade).isdigit():
                assert validar_codigo_cidade(
                    self.endereco_cidade
                ), f"Código de cidade inválido: {self.endereco_cidade}"

        if isinstance(self.endereco_tipo_logradouro, str):
            if self.endereco_tipo_logradouro.upper() in TipoLogradouro.__members__:
                self.endereco_tipo_logradouro = TipoLogradouro[
                    self.endereco_tipo_logradouro.upper()
                ]
            else:
                self.endereco_tipo_logradouro = TipoLogradouro(
                    self.endereco_tipo_logradouro.upper()
                )

        assert (
            self.aliquota_servicos >= 0 and self.aliquota_servicos <= 1
        ), "A alíquota de serviços deve ser um valor entre 0 e 1"

        if isinstance(self.codigo_servico, int):
            self.codigo_servico = str(self.codigo_servico).zfill(4)
        elif isinstance(self.codigo_servico, str):
            assert len(self.codigo_servico) in [
                4,
                5,
            ], "Código de serviço deve ter 4 ou 5 dígitos"

        # assert (
        #     self.codigo_servico in codigos_de_servico_validos
        # ), f"Código de serviço inválido, os códigos válidos são: {codigos_de_servico_validos}"
        assert self.email_tomador is None or validar_email(
            self.email_tomador
        ), f"Email do tomador com formato inválido: {self.email_tomador}"
        assert (
            isinstance(self.valor_servicos_centavos, int)
            and self.valor_servicos_centavos >= 0
        ), "O valor de serviços deve ser um valor decimal maior ou igual a zero"
        assert self.valor_deducoes_centavos is None or (
            isinstance(self.valor_deducoes_centavos, int)
            and self.valor_deducoes_centavos >= 0
        ), "O valor de deduções deve ser um valor decimal maior ou igual a zero"
        assert self.valor_pis_centavos is None or (
            isinstance(self.valor_pis_centavos, int) and self.valor_pis_centavos >= 0
        ), "O valor de PIS deve ser um valor decimal maior ou igual a zero"
        assert self.valor_cofins_centavos is None or (
            isinstance(self.valor_cofins_centavos, int)
            and self.valor_cofins_centavos >= 0
        ), "O valor de COFINS deve ser um valor decimal maior ou igual a zero"
        assert self.valor_inss_centavos is None or (
            isinstance(self.valor_inss_centavos, int) and self.valor_inss_centavos >= 0
        ), "O valor de INSS deve ser um valor decimal maior ou igual a zero"
        assert self.valor_ir_centavos is None or (
            isinstance(self.valor_ir_centavos, int) and self.valor_ir_centavos >= 0
        ), "O valor de IR deve ser um valor decimal maior ou igual a zero"
        assert self.valor_csll_centavos is None or (
            isinstance(self.valor_csll_centavos, int) and self.valor_csll_centavos >= 0
        ), "O valor de CSLL deve ser um valor decimal maior ou igual a zero"
        assert self.valor_carga_tributaria_centavos is None or (
            isinstance(self.valor_carga_tributaria_centavos, int)
            and self.valor_carga_tributaria_centavos >= 0
        ), "O valor da carga tributária deve ser um valor decimal maior ou igual a zero"
        assert self.valor_total_recebido_centavos is None or (
            isinstance(self.valor_total_recebido_centavos, int)
            and self.valor_total_recebido_centavos >= 0
        ), "O valor total recebido deve ser um valor decimal maior ou igual a zero"
        assert (
            self.valor_carga_tributaria_centavos is None
            or self.valor_carga_tributaria_centavos >= 0
        ), "O valor da carga tributária deve ser maior ou igual a zero"
        assert (
            self.valor_servicos_centavos
            - (self.valor_deducoes_centavos or 0)
            - (self.valor_pis_centavos or 0)
            - (self.valor_cofins_centavos or 0)
            - (self.valor_inss_centavos or 0)
            - (self.valor_ir_centavos or 0)
            - (self.valor_csll_centavos or 0)
            >= 0
        ), "A soma dos valores não pode ser negativa"

        if self.serie_rps is not None:
            self.serie_rps = self.serie_rps.strip()
            assert (
                len(self.serie_rps) <= 5
            ), "A série do RPS deve ter no máximo 5 caracteres"

        if self.inscricao_municipal_tomador is not None:
            assert (
                self.inscricao_municipal_tomador.isdigit()
                and len(self.inscricao_municipal_tomador) == 8
            ), "Inscrição municipal do tomador deve ter 8 dígitos"
            assert (
                self.tomador is not None
            ), "Ao preencher a inscrição municipal do tomador, o CPF ou CNPJ do tomador deve ser preenchido"

        if self.inscricao_municipal_intermediario is not None:
            assert (
                self.inscricao_municipal_intermediario.isdigit()
                and len(self.inscricao_municipal_intermediario) == 8
            ), "Inscrição municipal do intermediário deve ter 8 dígitos"
            assert (
                self.intermediario is not None
            ), "Ao preencher a inscrição municipal do intermediário, o CPF ou CNPJ do intermediário deve ser preenchido"

        if self.intermediario is not None:
            assert (
                self.iss_retido_intermediario is not None
            ), "Ao preencher o intermediário, o ISS retido do intermediário deve ser preenchido"

        assert self.email_intermediario is None or validar_email(
            self.email_intermediario
        ), f"Email do intermediário com formato inválido: {self.email_intermediario}"

        assert (
            self.percentual_carga_tributaria is None
            or isinstance(self.percentual_carga_tributaria, float)
            and self.percentual_carga_tributaria >= 0
            and self.percentual_carga_tributaria <= 1
        ), "O percentual da carga tributária deve ser um valor entre 0 e 1"

        assert (
            self.fonte_carga_tributaria is None
            or isinstance(self.fonte_carga_tributaria, str)
            and len(self.fonte_carga_tributaria) <= 10
        ), "A fonte da carga tributária deve ter no máximo 10 caracteres"

    def gerar_string_xml(self, assinador: Assinador) -> str:
        template = load_template("RPS")
        return template.render(
            inscricao_prestador=str(self.inscricao_prestador).zfill(8),
            serie_rps=self.serie_rps,
            numero_rps=self.numero_rps,
            tipo_rps=self.tipo_rps,
            data_emissao=self.data_emissao,
            status_rps=self.status_rps,
            inscricao_estadual_tomador=self.inscricao_estadual_tomador,
            tributacao_rps=self.tributacao_rps,
            valor_servicos=f"{self.valor_servicos_centavos / 100:.2f}",
            valor_deducoes=f"{self.valor_deducoes_centavos / 100:.2f}"
            if self.valor_deducoes_centavos is not None
            else None,
            valor_pis=f"{self.valor_pis_centavos / 100:.2f}"
            if self.valor_pis_centavos is not None
            else None,
            valor_cofins=f"{self.valor_cofins_centavos / 100:.2f}"
            if self.valor_cofins_centavos is not None
            else None,
            valor_inss=f"{self.valor_inss_centavos / 100:.2f}"
            if self.valor_inss_centavos is not None
            else None,
            valor_ir=f"{self.valor_ir_centavos / 100:.2f}"
            if self.valor_ir_centavos is not None
            else None,
            valor_csll=f"{self.valor_csll_centavos / 100:.2f}"
            if self.valor_csll_centavos is not None
            else None,
            codigo_servico=self.codigo_servico,
            aliquota_servicos=self.aliquota_servicos,
            iss_retido=str(self.iss_retido).lower(),
            tomador=self.tomador,
            tomador_tipo=self.tomador_tipo,
            razao_social_tomador=self.razao_social_tomador,
            endereco_tipo_logradouro=self.endereco_tipo_logradouro.value.capitalize()
            if self.endereco_tipo_logradouro is not None
            else None,
            endereco_logradouro=self.endereco_logradouro,
            endereco_numero=self.endereco_numero,
            endereco_complemento=self.endereco_complemento,
            endereco_bairro=self.endereco_bairro,
            endereco_cidade=self.endereco_cidade,
            endereco_uf=self.endereco_uf.value
            if self.endereco_uf is not None
            else None,
            endereco_cep=self.endereco_cep,
            email_tomador=self.email_tomador,
            discriminacao=self.discriminacao,
            assinatura=self.assinatura(assinador),
            intermediario=self.intermediario,
            intermediario_tipo=self.intermediario_tipo,
            inscricao_municipal_intermediario=self.inscricao_municipal_intermediario,
            iss_retido_intermediario=self.iss_retido_intermediario,
            email_intermediario=self.email_intermediario,
            percentual_carga_tributaria=self.percentual_carga_tributaria,
            fonte_carga_tributaria=self.fonte_carga_tributaria,
            codigo_cei=self.codigo_cei,
            matricula_obra=self.matricula_obra,
            municipio_prestacao=self.municipio_prestacao,
            numero_encapsulamento=self.numero_encapsulamento,
            inscricao_municipal_tomador=self.inscricao_municipal_tomador,
            valor_carga_tributaria=f"{self.valor_carga_tributaria_centavos / 100:.2f}"
            if self.valor_carga_tributaria_centavos is not None
            else None,
            valor_total_recebido=f"{self.valor_total_recebido_centavos / 100:.2f}"
            if self.valor_total_recebido_centavos is not None
            else None,
        )

    @staticmethod
    def ler_txt(conteudo: str) -> List["RPS"]:
        lista_rps = []
        lines = conteudo.splitlines()
        inscricao_prestador = None

        for line in lines:
            if line.startswith("1"):
                inscricao_prestador = int(line[4:12])
            elif line.startswith("6"):
                if inscricao_prestador is None:
                    continue

                tipo_rps = line[1:6].strip()
                serie_rps = line[6:11].strip()
                numero_rps = int(line[11:23])
                data_emissao = parse(line[23:31]).date()
                status_rps = line[31:32]

                valor_servicos_centavos = int(line[32:47])
                valor_deducoes_centavos = int(line[47:62])

                codigo_servico = line[62:67].strip()

                aliquota_servicos = int(line[67:71]) / 10000

                iss_retido = line[71:72] == "1"
                tipo_tomador = line[72:73]

                tomador_cpf_cnpj = line[73:87].strip()

                # If Type 1 (CPF), ensure it is treated as 11 digits by stripping leading zeros/padding
                if tipo_tomador == "1":
                    # Taking the last 11 digits is safer if it was left-padded with zeros
                    if len(tomador_cpf_cnpj) > 11:
                        tomador_cpf_cnpj = tomador_cpf_cnpj[-11:]

                try:
                    tomador_cpf_cnpj = normalizar_cpf_ou_cnpj(tomador_cpf_cnpj)
                except ValueError:
                    tomador_cpf_cnpj = None

                im_tomador = line[87:95].strip()
                ie_tomador = line[95:107].strip()

                razao_social_tomador = line[107:182].strip()

                endereco_tipo_logradouro_raw = line[182:185].strip().rstrip(".")
                try:
                    if (
                        endereco_tipo_logradouro_raw.upper()
                        in TipoLogradouro.__members__
                    ):
                        endereco_tipo_logradouro = TipoLogradouro[
                            endereco_tipo_logradouro_raw.upper()
                        ]
                    else:
                        endereco_tipo_logradouro = TipoLogradouro(
                            endereco_tipo_logradouro_raw.upper()
                        )
                except ValueError:
                    endereco_tipo_logradouro = None
                endereco_logradouro = line[185:235].strip()
                endereco_numero = line[235:245].strip()
                endereco_complemento = line[245:275].strip()
                endereco_bairro = line[275:305].strip()

                # Cidade (Nome) is at 306-355
                endereco_cidade = line[305:355].strip()

                endereco_uf = line[355:357].strip()
                endereco_cep = line[357:365].strip()

                email_tomador_raw = line[365:440].strip()
                email_tomador = (
                    email_tomador_raw if "@" in email_tomador_raw else None
                )

                # Layout V.002 Fields (Positions 441+)
                valor_pis_centavos = int(line[440:455])
                valor_cofins_centavos = int(line[455:470])
                valor_inss_centavos = int(line[470:485])
                valor_ir_centavos = int(line[485:500])
                valor_csll_centavos = int(line[500:515])

                valor_carga_tributaria_centavos = int(line[515:530])
                percentual_carga_tributaria = int(line[530:535]) / 10000
                fonte_carga_tributaria = line[535:545].strip()

                codigo_cei = line[545:557].strip()
                matricula_obra = line[557:569].strip()
                municipio_prestacao = line[569:576].strip()
                numero_encapsulamento = line[576:586].strip()
                
                # Reserved 587-596

                valor_total_recebido_centavos = line[596:611].strip()

                # Reserved 612-786

                discriminacao = line[786:].strip()

                rps = RPS(
                    inscricao_prestador=inscricao_prestador,
                    numero_rps=numero_rps,
                    tipo_rps=tipo_rps,
                    data_emissao=data_emissao,
                    status_rps=status_rps,
                    tributacao_rps="T",  # Defaulting or needs extraction?
                    # WARNING: 'tributacao_rps' was missing in V.002 extraction in previous code too?
                    # In V.001/V.002 header logic:
                    # Pos 32: Situação do RPS (T, F, A, B...) -> This maps to 'tributacao_rps' in RPS dataclass?
                    # In RPS dataclass: status_rps is Literal["N", "C"] (Normal, Cancelado).
                    # But in Manual: Pos 32 is "Situação do RPS" with values T, F, A, B...
                    # Wait. Manual says:
                    # 6) Situação do RPS (32-32): T, F, A, B... (Taxation Type).
                    # BUT RPS Dataclass has `status_rps` AND `tributacao_rps`.
                    # Let's check RPS Dataclass:
                    # `status_rps`: Literal["N", "C"]
                    # `tributacao_rps`: Literal["T", "F", ...]
                    #
                    # In Manual V.001/V.002:
                    # Field 6 "Situação do RPS" contains T, F, A, B, C (Cancelado)...
                    # So if it is 'C', it is Cancelled. If it is 'T', it is Normal & Taxed inside SP.
                    # The `RPS` object separates Status (Normal/Cancelled) and Taxation.
                    # Logic needed:
                    # If line[31] == 'C': status='C', tributacao=? (Maybe previous valid one or None?)
                    # If line[31] != 'C': status='N', tributacao=line[31]
                    #
                    # Re-reading Manual 2.3.1:
                    # "Situação do RPS ... C – Cancelado"
                    # "T – Tributado em São Paulo"
                    #
                    # So line[31] (pos 32) holds the Taxation info OR Cancelled status.
                    #
                    # I will implement logic to split this.
                    #
                    valor_servicos_centavos=valor_servicos_centavos,
                    valor_deducoes_centavos=valor_deducoes_centavos,
                    codigo_servico=codigo_servico,
                    aliquota_servicos=aliquota_servicos,
                    iss_retido=iss_retido,
                    serie_rps=serie_rps,
                    tomador=tomador_cpf_cnpj,
                    razao_social_tomador=razao_social_tomador,
                    endereco_tipo_logradouro=endereco_tipo_logradouro,
                    endereco_logradouro=endereco_logradouro,
                    endereco_numero=endereco_numero,
                    endereco_complemento=endereco_complemento,
                    endereco_bairro=endereco_bairro,
                    endereco_cidade=endereco_cidade,
                    endereco_uf=endereco_uf,
                    endereco_cep=endereco_cep,
                    email_tomador=email_tomador,
                    discriminacao=discriminacao,
                    valor_pis_centavos=valor_pis_centavos,
                    valor_cofins_centavos=valor_cofins_centavos,
                    valor_inss_centavos=valor_inss_centavos,
                    valor_ir_centavos=valor_ir_centavos,
                    valor_csll_centavos=valor_csll_centavos,
                    valor_carga_tributaria_centavos=valor_carga_tributaria_centavos,
                    percentual_carga_tributaria=percentual_carga_tributaria,
                    fonte_carga_tributaria=fonte_carga_tributaria,
                    codigo_cei=int(codigo_cei) if codigo_cei else None,
                    matricula_obra=int(matricula_obra) if matricula_obra else None,
                    municipio_prestacao=int(municipio_prestacao)
                    if municipio_prestacao
                    else None,
                    numero_encapsulamento=int(numero_encapsulamento)
                    if numero_encapsulamento
                    else None,
                    valor_total_recebido_centavos=int(valor_total_recebido_centavos)
                    if valor_total_recebido_centavos
                    else None,
                    inscricao_municipal_tomador=im_tomador
                    if im_tomador and im_tomador != "00000000"
                    else None,
                    inscricao_estadual_tomador=ie_tomador
                    if ie_tomador and ie_tomador != "000000000000"
                    else None,
                )
                
                # Correction for status/tributacao logic inside the object construction above
                if line[31] == 'C':
                    rps.status_rps = 'C'
                    # Tributacao is mandatory in RPS dataclass, but meaningless if cancelled?
                    # We'll default to 'T' if cancelled, or leave it if it allows.
                    # The dataclass definition says `tributacao_rps: Literal[...]`
                    rps.tributacao_rps = 'T' 
                else:
                    rps.status_rps = 'N'
                    rps.tributacao_rps = line[31]

                lista_rps.append(rps)

        return lista_rps

    def assinatura(self, assinador: Assinador) -> str:
        template = ""
        template += str(self.inscricao_prestador).zfill(8)
        template += self.serie_rps.upper() + (5 - len(self.serie_rps)) * " "
        template += str(self.numero_rps).zfill(12)
        template += self.data_emissao.strftime("%Y%m%d").upper()
        template += self.tributacao_rps
        template += self.status_rps
        template += self.iss_retido == "true" and "S" or "N"
        template += str(self.valor_servicos_centavos).zfill(15)
        template += str(self.valor_deducoes_centavos).zfill(15)
        template += self.codigo_servico.zfill(5)
        if self.tomador_tipo == "CPF":
            template += "1"
        elif self.tomador_tipo == "CNPJ":
            template += "2"
        elif self.tomador_tipo is None:
            template += "3"
        template += (
            (self.tomador or "")
            .replace(".", "")
            .replace("-", "")
            .replace("/", "")
            .zfill(14)
        )

        if self.intermediario is not None:
            if self.intermediario_tipo == "CPF":
                template += "1"
            elif self.intermediario_tipo == "CNPJ":
                template += "2"
            template += (
                (self.intermediario or "")
                .replace(".", "")
                .replace("-", "")
                .replace("/", "")
                .zfill(14)
            )

            template += self.iss_retido_intermediario == "true" and "S" or "N"

        template_bytes = template.encode("ascii")

        signed_template = assinador.assinar_bytes_rsa_sh1(template_bytes)
        return base64.b64encode(signed_template).decode("ascii")

    @property
    def tomador_tipo(self) -> Optional[Literal["CPF", "CNPJ"]]:
        return cpf_ou_cnpj(self.tomador) if self.tomador is not None else None

    @property
    def intermediario_tipo(self) -> Optional[Literal["CPF", "CNPJ"]]:
        return (
            cpf_ou_cnpj(self.intermediario) if self.intermediario is not None else None
        )


@dataclass
class EnvioRPS(RPS, Pedido, Remessa):
    def gerar_xml(self, assinador: Assinador) -> Element:
        xml = self.template.render(
            remetente=self.remetente,
            remetente_tipo=self.remetente_tipo,
            rps=self.gerar_string_xml(assinador),
        )

        return fromstring(xml)

    @property
    def nome_metodo(self):
        return "EnvioRPS"


@dataclass
class RetornoEnvioRpsLote(Retorno):
    numero_lote: int
    inscricao_prestador: int
    remetente: str
    data_envio_lote: date
    qtd_notas_processadas: int
    tempo_processamento: int
    valor_total_servicos: int
    chaves_nfe_rps: List[ChaveNFeRPS]

    @staticmethod
    def ler_xml(xml: Element) -> "RetornoEnvioRps":
        if xml.find(".//Sucesso").text == "false":
            raise ErroEnvioRps(
                codigo=xml.find(".//Codigo").text,
                descricao=xml.find(".//Descricao").text,
            )
        return RetornoEnvioRpsLote(
            numero_lote=int(xml.find(".//NumeroLote").text),
            inscricao_prestador=int(xml.find(".//InscricaoPrestador").text),
            remetente=xml.find(".//CPFCNPJRemetente").find(".//CNPJ").text,
            data_envio_lote=parse(xml.find(".//DataEnvioLote").text).date(),
            qtd_notas_processadas=int(xml.find(".//QtdNotasProcessadas").text),
            tempo_processamento=int(xml.find(".//TempoProcessamento").text),
            valor_total_servicos=int(xml.find(".//ValorTotalServicos").text),
            chaves_nfe_rps=[
                ChaveNFeRPS.ler_xml(retorno)
                for retorno in xml.findall(".//ChaveNFeRPS")
            ],
        )


@dataclass
class EnvioLoteRPS(Pedido, Remessa):
    transacao: bool
    data_inicio_periodo_transmitido: date
    data_fim_periodo_transmitido: date
    lista_rps: List[RPS]

    teste: bool = False
    """
    Define se o lote é um teste ou produção.
    """

    def __post_init__(self):
        if isinstance(self.data_fim_periodo_transmitido, str):
            self.data_fim_periodo_transmitido = parse(
                self.data_fim_periodo_transmitido
            ).date()

        if isinstance(self.data_inicio_periodo_transmitido, str):
            self.data_inicio_periodo_transmitido = parse(
                self.data_inicio_periodo_transmitido
            ).date()

        for idx, rps in enumerate(self.lista_rps):
            if isinstance(rps, dict):
                self.lista_rps[idx] = RPS(**rps)

        assert len(self.lista_rps) > 0, "Deve haver pelo menos um RPS no lote"
        assert len(self.lista_rps) <= 50, "O lote não pode ter mais de 50 RPS"

    def gerar_xml(self, assinador: Assinador) -> Element:
        xml = self.template.render(
            remetente=self.remetente,
            remetente_tipo=self.remetente_tipo,
            transacao=str(self.transacao).lower(),
            dt_inicio=str(self.data_inicio_periodo_transmitido),
            dt_fim=str(self.data_fim_periodo_transmitido),
            qtd_rps=self.quantidade_rps,
            valor_total_servicos=f"{self.valor_total_servicos:.2f}",
            valor_total_deducoes=f"{self.valor_total_deducoes:.2f}",
            lista_rps=[rps.gerar_string_xml(assinador) for rps in self.lista_rps],
        )

        return fromstring(xml)

    @property
    def quantidade_rps(self):
        return len(self.lista_rps)

    @property
    def valor_total_servicos(self):
        return sum(rps.valor_servicos_centavos for rps in self.lista_rps) / 100

    @property
    def valor_total_deducoes(self):
        return sum(rps.valor_deducoes_centavos for rps in self.lista_rps) / 100

    @property
    def remetente_tipo(self) -> Literal["CPF", "CNPJ"]:
        return cpf_ou_cnpj(self.remetente)

    @property
    def metodo(self) -> str:
        if self.teste:
            return "TesteEnvioLoteRPS"
        else:
            return "EnvioLoteRPS"
