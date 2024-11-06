from dataclasses import dataclass
from typing import Literal
from lxml.etree import Element, SubElement, tostring
from abstra_notas.validacoes.email import validar_email
from abstra_notas.validacoes.cidades import validar_codigo_cidade, normalizar_uf
from abstra_notas.validacoes.cep import normalizar_cep
from .codigos_de_servico import codigos_de_servico_validos
from datetime import date
from abc import ABC, abstractmethod
from decimal import Decimal, getcontext
from .tipos_comuns import Cabecalho

getcontext().prec = 2


class StatusRPS(ABC):
    class _Normal(ABC):
        def gerar_string(self) -> str:
            return "N"

    class _Cancelado(ABC):
        def gerar_string(self) -> str:
            return "C"

    NORMAL = _Normal()
    CANCELADO = _Cancelado()

    @abstractmethod
    def gerar_string(self) -> str:
        raise NotImplementedError

    @staticmethod
    def parse_string(string: str) -> "StatusRPS":
        if string == "N":
            return StatusRPS.NORMAL
        if string == "C":
            return StatusRPS.CANCELADO
        raise ValueError(f"Status de RPS inválido: {string}")

    def __eq__(self, value):
        return (
            isinstance(value, self.__class__)
            and self.gerar_string() == value.gerar_string()
        )


class TipoRPS(ABC):
    class _RPSM(ABC):
        def gerar_string(self) -> str:
            return "RPS-M"

    class _RPS(ABC):
        def gerar_string(self) -> str:
            return "RPS"

    class _RPSC(ABC):
        def gerar_string(self) -> str:
            return "RPS-C"

    RPS_M = _RPSM()
    """
    Recibo provisório de serviços provenientes de nota fiscal conjugada (mista)
    """

    RPS = _RPS()
    """
    Recibo provisório de serviços
    """

    RPS_C = _RPSC()
    """
    Recibo provisório de cupom fiscal
    """

    @abstractmethod
    def gerar_string(self) -> str:
        raise NotImplementedError

    @staticmethod
    def parse_string(string: str) -> "TipoRPS":
        if string == "RPS-M":
            return TipoRPS.RPS_M
        if string == "RPS":
            return TipoRPS.RPS
        if string == "RPS-C":
            return TipoRPS.RPS_C
        raise ValueError(f"Tipo de RPS inválido: {string}")

    def __eq__(self, value):
        return (
            isinstance(value, self.__class__)
            and self.gerar_string() == value.gerar_string()
        )


class TributacaoRPS(ABC):
    class _T(ABC):
        def gerar_string(self) -> str:
            return "T"

    class _F(ABC):
        def gerar_string(self) -> str:
            return "F"

    class _A(ABC):
        def gerar_string(self) -> str:
            return "A"

    class _B(ABC):
        def gerar_string(self) -> str:
            return "B"

    class _D(ABC):
        def gerar_string(self) -> str:
            return "D"

    class _M(ABC):
        def gerar_string(self) -> str:
            return "M"

    class _N(ABC):
        def gerar_string(self) -> str:
            return "N"

    class _R(ABC):
        def gerar_string(self) -> str:
            return "R"

    class _S(ABC):
        def gerar_string(self) -> str:
            return "S"

    class _X(ABC):
        def gerar_string(self) -> str:
            return "X"

    class _V(ABC):
        def gerar_string(self) -> str:
            return "V"

    class _P(ABC):
        def gerar_string(self) -> str:
            return "P"

    T = _T()
    """
    Tributado em São Paulo
    """

    F = _F()
    """
    Tributado Fora de São Paulo
    """

    A = _A()
    """
    Tributado em São Paulo, porém Isento
    """

    B = _B()
    """
    Tributado Fora de São Paulo, porém Isento
    """

    D = _D()
    """
    Tributado em São Paulo com isenção parcial
    """

    M = _M()
    """
    Tributado em São Paulo, porém com indicação de imunidade subjetiva
    """

    N = _N()
    """
    Tributado Fora de São Paulo, porém com indicação de imunidade subjetiva
    """

    R = _R()
    """
    Tributado em São Paulo, porém com indicação de imunidade objetiva
    """

    S = _S()
    """
    Tributado fora de São Paulo, porém com indicação de imunidade objetiva
    """

    X = _X()
    """
    Tributado em São Paulo, porém Exigibilidade Suspensa
    """

    V = _V()
    """
    Tributado Fora de São Paulo, porém Exigibilidade Suspensa
    """

    P = _P()
    """
    Exportação de Serviços
    """

    @abstractmethod
    def gerar_string(self) -> str:
        raise NotImplementedError

    @staticmethod
    def parse_string(string: str) -> "TributacaoRPS":
        if string == "T":
            return TributacaoRPS.T
        if string == "F":
            return TributacaoRPS.F
        if string == "A":
            return TributacaoRPS.A
        if string == "B":
            return TributacaoRPS.B
        if string == "D":
            return TributacaoRPS.D
        if string == "M":
            return TributacaoRPS.M
        if string == "N":
            return TributacaoRPS.N
        if string == "R":
            return TributacaoRPS.R
        if string == "S":
            return TributacaoRPS.S
        if string == "X":
            return TributacaoRPS.X
        if string == "V":
            return TributacaoRPS.V
        if string == "P":
            return TributacaoRPS.P
        raise ValueError(f"Tributação de RPS inválida: {string}")

    def __eq__(self, value):
        return (
            isinstance(value, self.__class__)
            and self.gerar_string() == value.gerar_string()
        )


@dataclass
class ChaveRPS:
    inscricao_prestador: str
    serie_rps: str
    numero_rps: int

    def gerar_xml(self) -> Element:
        chaverps = Element("ChaveRPS")
        SubElement(chaverps, "InscricaoPrestador").text = self.inscricao_prestador
        SubElement(chaverps, "SerieRPS").text = self.serie_rps
        SubElement(chaverps, "NumeroRPS").text = str(self.numero_rps)
        return chaverps

    @staticmethod
    def parse_xml(element: Element) -> "ChaveRPS":
        inscricao_prestador = element.find("InscricaoPrestador").text
        serie_rps = element.find("SerieRPS").text
        numero_rps = int(element.find("NumeroRPS").text)
        return ChaveRPS(
            inscricao_prestador=inscricao_prestador,
            serie_rps=serie_rps,
            numero_rps=numero_rps,
        )


@dataclass
class CPFCNPJTomador:
    tipo: Literal["CPF", "CNPJ"]
    numero: str

    def gerar_xml(self) -> Element:
        cpfcnpjtomador = Element("CPFCNPJTomador")
        SubElement(cpfcnpjtomador, self.tipo).text = self.numero
        return cpfcnpjtomador

    @staticmethod
    def parse_xml(element: Element) -> "CPFCNPJTomador":
        tipo = element[0].tag
        numero = element.find(tipo).text
        return CPFCNPJTomador(tipo=tipo, numero=numero)


@dataclass
class EnderecoTomador:
    tipo_logradouro: str
    logradouro: str
    numero_endereco: str
    complemento_endereco: str
    bairro: str
    cidade: int
    uf: str
    cep: str

    def __post_init__(self):
        self.cep = normalizar_cep(self.cep)
        self.uf = normalizar_uf(self.uf)
        assert validar_codigo_cidade(
            self.cidade
        ), f"Código de cidade inválido: {self.cidade}"

    def gerar_xml(self) -> Element:
        enderecotomador = Element("EnderecoTomador")
        SubElement(enderecotomador, "TipoLogradouro").text = self.tipo_logradouro
        SubElement(enderecotomador, "Logradouro").text = self.logradouro
        SubElement(enderecotomador, "NumeroEndereco").text = self.numero_endereco
        SubElement(
            enderecotomador, "ComplementoEndereco"
        ).text = self.complemento_endereco
        SubElement(enderecotomador, "Bairro").text = self.bairro
        SubElement(enderecotomador, "Cidade").text = str(self.cidade)
        SubElement(enderecotomador, "UF").text = self.uf
        SubElement(enderecotomador, "CEP").text = self.cep
        return enderecotomador

    @staticmethod
    def parse_xml(element: Element) -> "EnderecoTomador":
        tipo_logradouro = element.find("TipoLogradouro").text
        logradouro = element.find("Logradouro").text
        numero_endereco = element.find("NumeroEndereco").text
        complemento_endereco = element.find("ComplementoEndereco").text
        bairro = element.find("Bairro").text
        cidade = int(element.find("Cidade").text)
        uf = element.find("UF").text
        cep = element.find("CEP").text
        return EnderecoTomador(
            tipo_logradouro=tipo_logradouro,
            logradouro=logradouro,
            numero_endereco=numero_endereco,
            complemento_endereco=complemento_endereco,
            bairro=bairro,
            cidade=cidade,
            uf=uf,
            cep=cep,
        )


@dataclass
class RPS:
    assinatura: str
    chave_rps: ChaveRPS
    tipo_rps: TipoRPS
    data_emissao: date
    status_rps: StatusRPS
    tributacao_rps: TributacaoRPS
    valor_servicos: Decimal
    valor_deducoes: Decimal
    valor_pis: Decimal
    valor_cofins: Decimal
    valor_inss: Decimal
    valor_ir: Decimal
    valor_csll: Decimal
    codigo_servico: int
    aliquota_servicos: float
    iss_retido: bool
    cpf_cnpj_tomador: CPFCNPJTomador
    razao_social_tomador: str
    endereco_tomador: EnderecoTomador
    email_tomador: str
    discriminacao: str

    def __post_init__(self):
        assert (
            self.aliquota_servicos >= 0 and self.aliquota_servicos <= 1
        ), "A alíquota de serviços deve ser um valor entre 0 e 1"
        assert (
            self.codigo_servico in codigos_de_servico_validos
        ), f"Código de serviço inválido, os códigos válidos são: {codigos_de_servico_validos}"
        assert validar_email(
            self.email_tomador
        ), f"Email do tomador com formato inválido: {self.email_tomador}"
        assert isinstance(
            self.valor_servicos, (int, Decimal)
        ), "O valor de serviços deve ser um valor decimal"
        assert isinstance(
            self.valor_deducoes, (int, Decimal)
        ), "O valor de deduções deve ser um valor decimal"
        assert isinstance(
            self.valor_pis, (int, Decimal)
        ), "O valor de PIS deve ser um valor decimal"
        assert isinstance(
            self.valor_cofins, (int, Decimal)
        ), "O valor de COFINS deve ser um valor decimal"
        assert isinstance(
            self.valor_inss, (int, Decimal)
        ), "O valor de INSS deve ser um valor decimal"
        assert isinstance(
            self.valor_ir, (int, Decimal)
        ), "O valor de IR deve ser um valor decimal"
        assert isinstance(
            self.valor_csll, (int, Decimal)
        ), "O valor de CSLL deve ser um valor decimal"
        assert (
            self.valor_servicos >= 0
        ), "O valor de serviços deve ser maior ou igual a zero"
        assert (
            self.valor_deducoes >= 0
        ), "O valor de deduções deve ser maior ou igual a zero"
        assert self.valor_pis >= 0, "O valor de PIS deve ser maior ou igual a zero"
        assert (
            self.valor_cofins >= 0
        ), "O valor de COFINS deve ser maior ou igual a zero"
        assert self.valor_inss >= 0, "O valor de INSS deve ser maior ou igual a zero"
        assert self.valor_ir >= 0, "O valor de IR deve ser maior ou igual a zero"
        assert self.valor_csll >= 0, "O valor de CSLL deve ser maior ou igual a zero"
        self.valor_servicos = Decimal(self.valor_servicos)
        self.valor_deducoes = Decimal(self.valor_deducoes)
        self.valor_pis = Decimal(self.valor_pis)
        self.valor_cofins = Decimal(self.valor_cofins)
        self.valor_inss = Decimal(self.valor_inss)
        self.valor_ir = Decimal(self.valor_ir)
        self.valor_csll = Decimal(self.valor_csll)
        assert (
            self.valor_servicos
            - self.valor_deducoes
            - self.valor_pis
            - self.valor_cofins
            - self.valor_inss
            - self.valor_ir
            - self.valor_csll
            >= 0
        ), "A soma dos valores não pode ser negativa"

    def gerar_xml(self) -> Element:
        rps = Element("RPS")
        SubElement(rps, "Assinatura").text = self.assinatura
        chaverps = self.chave_rps.gerar_xml()
        rps.append(chaverps)
        SubElement(rps, "TipoRPS").text = self.tipo_rps.gerar_string()
        SubElement(rps, "DataEmissao").text = self.data_emissao.strftime("%Y-%m-%d")
        SubElement(rps, "StatusRPS").text = self.status_rps.gerar_string()
        SubElement(rps, "TributacaoRPS").text = self.tributacao_rps.gerar_string()
        SubElement(rps, "ValorServicos").text = str(self.valor_servicos)
        SubElement(rps, "ValorDeducoes").text = str(self.valor_deducoes)
        SubElement(rps, "ValorPIS").text = str(self.valor_pis)
        SubElement(rps, "ValorCOFINS").text = str(self.valor_cofins)
        SubElement(rps, "ValorINSS").text = str(self.valor_inss)
        SubElement(rps, "ValorIR").text = str(self.valor_ir)
        SubElement(rps, "ValorCSLL").text = str(self.valor_csll)
        SubElement(rps, "CodigoServico").text = str(self.codigo_servico)
        SubElement(rps, "AliquotaServicos").text = str(self.aliquota_servicos)
        SubElement(rps, "ISSRetido").text = "true" if self.iss_retido else "false"
        cpfcnpjtomador = self.cpf_cnpj_tomador.gerar_xml()
        rps.append(cpfcnpjtomador)
        SubElement(rps, "RazaoSocialTomador").text = self.razao_social_tomador
        enderecotomador = self.endereco_tomador.gerar_xml()
        rps.append(enderecotomador)
        SubElement(rps, "EmailTomador").text = self.email_tomador
        SubElement(rps, "Discriminacao").text = self.discriminacao
        return rps

    @staticmethod
    def parse_xml(element: Element) -> "RPS":
        return RPS(
            assinatura=element.find("Assinatura").text,
            chave_rps=ChaveRPS.parse_xml(element.find("ChaveRPS")),
            tipo_rps=TipoRPS.parse_string(element.find("TipoRPS").text),
            data_emissao=date.fromisoformat(element.find("DataEmissao").text),
            status_rps=StatusRPS.parse_string(element.find("StatusRPS").text),
            tributacao_rps=TributacaoRPS.parse_string(
                element.find("TributacaoRPS").text
            ),
            valor_servicos=Decimal(element.find("ValorServicos").text),
            valor_deducoes=Decimal(element.find("ValorDeducoes").text),
            valor_pis=Decimal(element.find("ValorPIS").text),
            valor_cofins=Decimal(element.find("ValorCOFINS").text),
            valor_inss=Decimal(element.find("ValorINSS").text),
            valor_ir=Decimal(element.find("ValorIR").text),
            valor_csll=Decimal(element.find("ValorCSLL").text),
            codigo_servico=int(element.find("CodigoServico").text),
            aliquota_servicos=float(element.find("AliquotaServicos").text),
            iss_retido=element.find("ISSRetido").text == "true",
            cpf_cnpj_tomador=CPFCNPJTomador.parse_xml(element.find("CPFCNPJTomador")),
            razao_social_tomador=element.find("RazaoSocialTomador").text,
            endereco_tomador=EnderecoTomador.parse_xml(element.find("EnderecoTomador")),
            email_tomador=element.find("EmailTomador").text,
            discriminacao=element.find("Discriminacao").text,
        )


@dataclass
class PedidoEnvioRPS:
    cabecalho: Cabecalho
    rps: RPS

    def gerar_xml(self) -> Element:
        pedidoenviorps = Element("PedidoEnvioRPS")
        cabecalho = self.cabecalho.gerar_xml()
        pedidoenviorps.append(cabecalho)
        rps = self.rps.gerar_xml()
        pedidoenviorps.append(rps)
        return pedidoenviorps

    def gerar_string(self) -> str:
        return tostring(self.gerar_xml(), encoding="unicode")

    @staticmethod
    def parse_xml(element: Element) -> "PedidoEnvioRPS":
        cabecalho = Cabecalho.parse_xml(element.find("Cabecalho"))
        rps = RPS.parse_xml(element.find("RPS"))
        return PedidoEnvioRPS(cabecalho=cabecalho, rps=rps)
