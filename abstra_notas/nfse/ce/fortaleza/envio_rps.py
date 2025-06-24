from dataclasses import dataclass
from typing import Literal, List, Optional
from lxml.etree import Element, fromstring, ElementBase
from dateutil.parser import parse
from abstra_notas.validacoes.email import validar_email
from abstra_notas.validacoes.cidades import validar_codigo_cidade, normalizar_uf, UF
from abstra_notas.validacoes.cpfcnpj import normalizar_cpf_ou_cnpj, cpf_ou_cnpj
from abstra_notas.validacoes.cep import normalizar_cep
from datetime import date
from .remessa import Remessa
from .pedido import Pedido
from .retorno import Retorno
from .templates import load_template
from abstra_notas.assinatura import Assinador
from .erro import Erro
from .validacoes import normalizar_inscricao_municipal


@dataclass
class ChaveNFeRPS(Retorno):
    numero_nfse: int
    codigo_verificacao: str
    numero_rps: int
    serie_rps: str
    
    def __post_init__(self):
        if isinstance(self.numero_nfse, str):
            self.numero_nfse = int(self.numero_nfse)
        if isinstance(self.numero_rps, str):
            self.numero_rps = int(self.numero_rps)

    @staticmethod
    def ler_xml(xml: ElementBase) -> "ChaveNFeRPS":
        return ChaveNFeRPS(
            numero_nfse=int(xml.find(".//Numero").text),
            codigo_verificacao=xml.find(".//CodigoVerificacao").text,
            numero_rps=int(xml.find(".//IdentificacaoRps/Numero").text),
            serie_rps=xml.find(".//IdentificacaoRps/Serie").text,
        )


@dataclass
class RetornoEnvioRps(ChaveNFeRPS):
    @staticmethod
    def ler_xml(xml: ElementBase) -> "RetornoEnvioRps":
        # Verifica se há erro na resposta
        lista_mensagens = xml.find(".//ListaMensagemRetorno")
        if lista_mensagens is not None:
            mensagem = lista_mensagens.find(".//MensagemRetorno")
            if mensagem is not None:
                raise ErroEnvioRps(
                    codigo=mensagem.find(".//Codigo").text,
                    descricao=mensagem.find(".//Mensagem").text,
                )
        
        # Se não há erro, processa a NFSe gerada
        nfse = xml.find(".//CompNfse/Nfse/InfNfse")
        if nfse is not None:
            return RetornoEnvioRps(
                numero_nfse=int(nfse.find(".//Numero").text),
                codigo_verificacao=nfse.find(".//CodigoVerificacao").text,
                numero_rps=int(nfse.find(".//DeclaracaoPrestacaoServico/InfDeclaracaoPrestacaoServico/Rps/IdentificacaoRps/Numero").text),
                serie_rps=nfse.find(".//DeclaracaoPrestacaoServico/InfDeclaracaoPrestacaoServico/Rps/IdentificacaoRps/Serie").text,
            )


@dataclass
class ErroEnvioRps(Erro):
    codigo: str
    descricao: str


@dataclass
class RPS:
    inscricao_prestador: str
    """
    Inscrição Municipal do Prestador em Fortaleza.
    """

    numero_rps: int
    """
    Número que identifica o RPS. Deve ser único para cada série de RPS.
    """

    serie_rps: str
    """
    Série do RPS.
    """

    data_emissao: date
    discriminacao: str
    
    codigo_servico: str
    """
    Código do serviço conforme lista de serviços de Fortaleza.
    """

    aliquota_servicos: float
    """
    Valor percentual da alíquota de serviços entre 0 e 1.
    """
    
    valor_servicos_centavos: int

    tipo_rps: Literal["1", "2", "3"] = "1"
    """
    1: RPS - Recibo Provisório de Serviços
    2: RPS-M - Recibo Provisório de Serviços proveniente de Nota Fiscal Mista
    3: RPS-C - Recibo Provisório de Serviços proveniente de Nota Fiscal Cupom
    """
    
    natureza_operacao: Literal["1", "2", "3", "4", "5", "6"] = "1"
    """
    1: Tributação no município
    2: Tributação fora do município
    3: Isenção
    4: Imune
    5: Exigibilidade suspensa por decisão judicial
    6: Exigibilidade suspensa por procedimento administrativo
    """

    iss_retido: bool = False
    valor_deducoes_centavos: int = 0

    # Dados do tomador
    tomador_cnpj_cpf: Optional[str] = None
    tomador_inscricao_municipal: Optional[str] = None
    tomador_razao_social: Optional[str] = None
    tomador_endereco_logradouro: Optional[str] = None
    tomador_endereco_numero: Optional[str] = None
    tomador_endereco_complemento: Optional[str] = None
    tomador_endereco_bairro: Optional[str] = None
    tomador_endereco_cidade: Optional[int] = None
    tomador_endereco_uf: Optional[UF] = None
    tomador_endereco_cep: Optional[str] = None
    tomador_telefone: Optional[str] = None
    tomador_email: Optional[str] = None

    # Valores opcionais de tributos
    valor_pis_centavos: Optional[int] = None
    valor_cofins_centavos: Optional[int] = None
    valor_inss_centavos: Optional[int] = None
    valor_ir_centavos: Optional[int] = None
    valor_csll_centavos: Optional[int] = None

    def __post_init__(self):
        if isinstance(self.data_emissao, str):
            self.data_emissao = parse(self.data_emissao).date()

        if self.tomador_endereco_cep is not None:
            self.tomador_endereco_cep = normalizar_cep(self.tomador_endereco_cep)

        if self.tomador_endereco_uf is not None:
            if isinstance(self.tomador_endereco_uf, str):
                self.tomador_endereco_uf = UF(normalizar_uf(self.tomador_endereco_uf))

        if self.tomador_cnpj_cpf is not None:
            self.tomador_cnpj_cpf = normalizar_cpf_ou_cnpj(self.tomador_cnpj_cpf)

        if self.tomador_endereco_cidade is not None:
            assert validar_codigo_cidade(
                self.tomador_endereco_cidade
            ), f"Código de cidade inválido: {self.tomador_endereco_cidade}"

        # Validações
        assert (
            self.aliquota_servicos >= 0 and self.aliquota_servicos <= 1
        ), "A alíquota de serviços deve ser um valor entre 0 e 1"

        assert self.tomador_email is None or validar_email(
            self.tomador_email
        ), f"Email do tomador com formato inválido: {self.tomador_email}"

        assert (
            isinstance(self.valor_servicos_centavos, int)
            and self.valor_servicos_centavos >= 0
        ), "O valor de serviços deve ser um valor inteiro maior ou igual a zero"

        self.inscricao_prestador = normalizar_inscricao_municipal(self.inscricao_prestador)

    def gerar_string_xml(self, assinador: Assinador) -> str:
        template = load_template("RPS")
        return template.render(
            inscricao_prestador=self.inscricao_prestador,
            numero_rps=self.numero_rps,
            serie_rps=self.serie_rps,
            tipo_rps=self.tipo_rps,
            data_emissao=self.data_emissao.strftime("%Y-%m-%d"),
            natureza_operacao=self.natureza_operacao,
            codigo_servico=self.codigo_servico,
            discriminacao=self.discriminacao,
            aliquota_servicos=self.aliquota_servicos,
            iss_retido=str(self.iss_retido).lower(),
            valor_servicos=f"{self.valor_servicos_centavos / 100:.2f}",
            valor_deducoes=f"{self.valor_deducoes_centavos / 100:.2f}" if self.valor_deducoes_centavos else "0.00",
            valor_pis=f"{self.valor_pis_centavos / 100:.2f}" if self.valor_pis_centavos else None,
            valor_cofins=f"{self.valor_cofins_centavos / 100:.2f}" if self.valor_cofins_centavos else None,
            valor_inss=f"{self.valor_inss_centavos / 100:.2f}" if self.valor_inss_centavos else None,
            valor_ir=f"{self.valor_ir_centavos / 100:.2f}" if self.valor_ir_centavos else None,
            valor_csll=f"{self.valor_csll_centavos / 100:.2f}" if self.valor_csll_centavos else None,
            tomador_cnpj_cpf=self.tomador_cnpj_cpf,
            tomador_tipo=self.tomador_tipo,
            tomador_inscricao_municipal=self.tomador_inscricao_municipal,
            tomador_razao_social=self.tomador_razao_social,
            tomador_endereco_logradouro=self.tomador_endereco_logradouro,
            tomador_endereco_numero=self.tomador_endereco_numero,
            tomador_endereco_complemento=self.tomador_endereco_complemento,
            tomador_endereco_bairro=self.tomador_endereco_bairro,
            tomador_endereco_cidade=self.tomador_endereco_cidade,
            tomador_endereco_uf=self.tomador_endereco_uf.value if self.tomador_endereco_uf else None,
            tomador_endereco_cep=self.tomador_endereco_cep,
            tomador_telefone=self.tomador_telefone,
            tomador_email=self.tomador_email,
        )

    @property
    def tomador_tipo(self) -> Optional[Literal["1", "2"]]:
        """
        1: CPF, 2: CNPJ
        """
        if self.tomador_cnpj_cpf is None:
            return None
        tipo = cpf_ou_cnpj(self.tomador_cnpj_cpf)
        return "1" if tipo == "CPF" else "2"


@dataclass
class EnvioRPS(RPS, Pedido, Remessa):
    def __post_init__(self):
        # Chama os __post_init__ das classes pai
        Remessa.__post_init__(self)
        RPS.__post_init__(self)
    
    def gerar_xml(self, assinador: Assinador) -> Element:
        xml = self.template.render(
            remetente=self.remetente,
            remetente_tipo="1" if self.remetente_tipo == "CPF" else "2",
            rps=self.gerar_string_xml(assinador),
        )
        return fromstring(xml.encode("utf-8"))

    @property
    def metodo(self) -> str:
        return "RecepcionarLoteRps"


@dataclass
class RetornoEnvioRpsLote(Retorno):
    numero_lote: str
    data_recebimento: date
    protocolo: str
    situacao: str
    
    @staticmethod
    def ler_xml(xml: Element) -> "RetornoEnvioRpsLote":
        # Verifica se há erro na resposta
        lista_mensagens = xml.find(".//ListaMensagemRetorno")
        if lista_mensagens is not None:
            mensagem = lista_mensagens.find(".//MensagemRetorno")
            if mensagem is not None:
                raise ErroEnvioRps(
                    codigo=mensagem.find(".//Codigo").text,
                    descricao=mensagem.find(".//Mensagem").text,
                )
        
        return RetornoEnvioRpsLote(
            numero_lote=xml.find(".//NumeroLote").text,
            data_recebimento=parse(xml.find(".//DataRecebimento").text).date(),
            protocolo=xml.find(".//Protocolo").text,
            situacao=xml.find(".//Situacao").text,
        )


@dataclass
class EnvioLoteRPS(Pedido, Remessa):
    numero_lote: str
    lista_rps: List[RPS]

    def __post_init__(self):
        # Chama o __post_init__ da classe pai
        Remessa.__post_init__(self)
        
        for idx, rps in enumerate(self.lista_rps):
            if isinstance(rps, dict):
                self.lista_rps[idx] = RPS(**rps)

        assert len(self.lista_rps) > 0, "Deve haver pelo menos um RPS no lote"
        assert len(self.lista_rps) <= 50, "O lote não pode ter mais de 50 RPS"

    def gerar_xml(self, assinador: Assinador) -> Element:
        xml = self.template.render(
            remetente=self.remetente,
            remetente_tipo="1" if self.remetente_tipo == "CPF" else "2",
            numero_lote=self.numero_lote,
            qtd_rps=self.quantidade_rps,
            lista_rps=[rps.gerar_string_xml(assinador) for rps in self.lista_rps],
        )
        return fromstring(xml.encode("utf-8"))

    @property
    def quantidade_rps(self):
        return len(self.lista_rps)

    @property
    def metodo(self) -> str:
        return "RecepcionarLoteRps"
