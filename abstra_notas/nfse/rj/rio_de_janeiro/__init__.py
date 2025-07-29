from dataclasses import dataclass
from datetime import datetime
from .base import Envio
from abstra_notas.validacoes.cnpj import normalizar_cnpj
from abstra_notas.validacoes.data import normalizar_data
from abstra_notas.validacoes.cpf import normalizar_cpf
from abstra_notas.validacoes.cidades import normalizar_uf
from abstra_notas.validacoes.cep import normalizar_cep
from abstra_notas.validacoes.email import validar_email
from abstra_notas.validacoes.telefone import normalizar_validar_telefone
from abstra_notas.validacoes.inscricao_municipal import normalizar_inscricao_municipal
from typing import List, Optional
from lxml.etree import ElementBase
from enum import Enum

def find_element(parent: ElementBase, tag_name: str):
    """
    Busca um elemento ignorando namespace.
    """
    element = parent.find(tag_name)
    if element is not None:
        return element
    
    # Se não encontrou, busca com qualquer namespace usando xpath
    try:
        xpath = f".//*[local-name()='{tag_name}']"
        elements = parent.xpath(xpath)
        if elements:
            return elements[0]
        else:
            pass
    except Exception as e:
        print(f"Erro no XPath para '{tag_name}': {e}")
        
    # Fallback: busca por todos os filhos e verifica o nome local
    for elem in parent.iter():
        if elem.tag.split('}')[-1] == tag_name: 
            return elem
    return None


def find_text(parent: ElementBase, tag_name: str, default: str = ''):
    """
    Busca o texto de um elemento ignorando namespace.
    """
    element = find_element(parent, tag_name)
    return element.text if element is not None else default


def find_all_elements(parent: ElementBase, tag_name: str):
    """
    Busca todos os elementos com o nome especificado ignorando namespace.
    """
    # Busca primeiro sem namespace
    elements = parent.findall(f".//{tag_name}")
    if elements:
        return elements
    
    # Se não encontrou, busca com qualquer namespace
    try:
        xpath = f".//*[local-name()='{tag_name}']"
        return parent.xpath(xpath)
    except Exception as e:
        print(f"Erro no XPath para '{tag_name}': {e}")
        print(f"XPath usado: .//*[local-name()='{tag_name}']")
        # Fallback: busca por todos os elementos e filtra pelo nome local
        result = []
        for elem in parent.iter():
            if elem.tag.split('}')[-1] == tag_name: 
                result.append(elem)
        return result

class TipoRps(Enum):
    """
    Tipo de RPS.
    """
    rps = '1'
    nota_fiscal_conjugada_mista = '2'
    cupom = '3'


@dataclass
class Valores:
    """
    xsd:complexType name="tcValores">
        <xsd:sequence>
            <xsd:element name="ValorServicos" type="tsValor" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="ValorDeducoes" type="tsValor" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="ValorPis" type="tsValor" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="ValorCofins" type="tsValor" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="ValorInss" type="tsValor" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="ValorIr" type="tsValor" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="ValorCsll" type="tsValor" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="IssRetido" type="tsSimNao" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="ValorIss" type="tsValor" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="ValorIssRetido" type="tsValor" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="OutrasRetencoes" type="tsValor" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="BaseCalculo" type="tsValor" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="Aliquota" type="tsAliquota" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="ValorLiquidoNfse" type="tsValor" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="DescontoIncondicionado" type="tsValor" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="DescontoCondicionado" type="tsValor" minOccurs="0" maxOccurs="1"/>
        </xsd:sequence>
    </xsd:complexType>
    """

    valor_servico_centavos: int
    valor_deducoes_centavos: Optional[int] = None
    valor_pis_centavos: Optional[int] = None
    valor_cofins_centavos: Optional[int] = None
    valor_inss_centavos: Optional[int] = None
    valor_ir_centavos: Optional[int] = None
    valor_csll_centavos: Optional[int] = None
    valor_iss_centavos: Optional[int] = None
    valor_iss_retido_centavos: Optional[int] = None
    outras_retencoes_centavos: Optional[int] = None
    base_calculo_centavos: Optional[int] = None
    aliquota_iss: Optional[float] = None
    valor_liquido_nfse_centavos: Optional[int] = None
    desconto_incondicionado_centavos: Optional[int] = None
    desconto_condicionado_centavos: Optional[int] = None

    def __post_init__(self):
        assert self.iss_retido_bool or self.valor_iss_centavos is not None, "Se o ISS não foi retido, o valor do ISS deve ser informado."

    @property
    def valor_servico(self):
        return f"{(self.valor_servico_centavos) / 100:.2f}"

    @property
    def valor_deducoes(self):
        if self.valor_deducoes_centavos is not None:
            return f"{(self.valor_deducoes_centavos) / 100:.2f}"
        return None

    @property
    def aliquota_iss_value(self):
        """
        Retorna a alíquota do ISS como string formatada.
        """
        if self.aliquota_iss is not None:
            return self.aliquota_iss
        return None


    @property
    def iss_retido_bool(self):
        """
        Retorna True se o ISS foi retido, False caso contrário.
        """
        return self.valor_iss_retido_centavos is not None and self.valor_iss_retido_centavos > 0

    @property
    def iss_retido_str(self):
        return '1' if self.iss_retido_bool else '2'

    @property
    def valor_pis(self):
        if self.valor_pis_centavos is not None:
            return f"{(self.valor_pis_centavos) / 100:.2f}"
        return None
    
    @property
    def valor_cofins(self):
        if self.valor_cofins_centavos is not None:
            return f"{(self.valor_cofins_centavos) / 100:.2f}"
        return None
    
    @property
    def valor_inss(self):
        if self.valor_inss_centavos is not None:
            return f"{(self.valor_inss_centavos) / 100:.2f}"
        return None
    
    @property
    def valor_ir(self):
        if self.valor_ir_centavos is not None:
            return f"{(self.valor_ir_centavos) / 100:.2f}"
        return None
    
    @property
    def valor_csll(self):
        if self.valor_csll_centavos is not None:
            return f"{(self.valor_csll_centavos) / 100:.2f}"
        return None
    
    @property
    def valor_iss(self):
        if self.valor_iss_centavos is not None:
            return f"{(self.valor_iss_centavos) / 100:.2f}"
        return None

    @property
    def valor_iss_retido(self):
        if self.valor_iss_retido_centavos is not None:
            return f"{(self.valor_iss_retido_centavos) / 100:.2f}"
        return None

    @property
    def outras_retencoes(self):
        if self.outras_retencoes_centavos is not None:
            return f"{(self.outras_retencoes_centavos) / 100:.2f}"
        return None
    
    @property
    def base_calculo(self):
        if self.base_calculo_centavos is not None:
            return f"{(self.base_calculo_centavos) / 100:.2f}"
        return None

    @property
    def valor_liquido_nfse(self):
        if self.valor_liquido_nfse_centavos is not None:
            return f"{(self.valor_liquido_nfse_centavos) / 100:.2f}"
        return None
    
    @property
    def valor_desconto_incondicionado(self):
        if self.desconto_incondicionado_centavos is not None:
            return f"{(self.desconto_incondicionado_centavos) / 100:.2f}"
        return None
    
    @property
    def valor_desconto_condicionado(self):
        if self.desconto_condicionado_centavos is not None:
            return f"{(self.desconto_condicionado_centavos) / 100:.2f}"
        return None


    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de Valores a partir de um elemento XML.
        """
        return cls(
            valor_servico_centavos=int(float(find_text(xml, 'ValorServicos', '0')) * 100),
            valor_deducoes_centavos=int(float(find_text(xml, 'ValorDeducoes', '0')) * 100) if find_element(xml, 'ValorDeducoes') is not None else None,
            valor_pis_centavos=int(float(find_text(xml, 'ValorPis', '0')) * 100) if find_element(xml, 'ValorPis') is not None else None,
            valor_cofins_centavos=int(float(find_text(xml, 'ValorCofins', '0')) * 100) if find_element(xml, 'ValorCofins') is not None else None,
            valor_inss_centavos=int(float(find_text(xml, 'ValorInss', '0')) * 100) if find_element(xml, 'ValorInss') is not None else None,
            valor_ir_centavos=int(float(find_text(xml, 'ValorIr', '0')) * 100) if find_element(xml, 'ValorIr') is not None else None,
            valor_csll_centavos=int(float(find_text(xml, 'ValorCsll', '0')) * 100) if find_element(xml, 'ValorCsll') is not None else None,
            valor_iss_centavos=int(float(find_text(xml, 'ValorIss', '0')) * 100) if find_element(xml, 'ValorIss') is not None else None,
            valor_iss_retido_centavos=int(float(find_text(xml, 'ValorIssRetido', '0')) * 100) if find_element(xml, 'ValorIssRetido') is not None else None,
            outras_retencoes_centavos=int(float(find_text(xml, 'OutrasRetencoes', '0')) * 100) if find_element(xml, 'OutrasRetencoes') is not None else None,
            base_calculo_centavos=int(float(find_text(xml, 'BaseCalculo', '0')) * 100) if find_element(xml, 'BaseCalculo') is not None else None,
            aliquota_iss=float(find_text(xml, 'Aliquota', '0.00').replace(',', '.')) if find_element(xml, 'Aliquota') is not None else None,
            valor_liquido_nfse_centavos=int(float(find_text(xml, 'ValorLiquidoNfse', '0')) * 100) if find_element(xml, 'ValorLiquidoNfse') is not None else None,
            desconto_incondicionado_centavos=int(float(find_text(xml, 'DescontoIncondicionado', '0')) * 100) if find_element(xml, 'DescontoIncondicionado') is not None else None,
            desconto_condicionado_centavos=int(float(find_text(xml, 'DescontoCondicionado', '0')) * 100) if find_element(xml, 'DescontoCondicionado') is not None else None,
        )



@dataclass
class DadosServico:
    """
    <xsd:complexType name="tcDadosServico">
        <xsd:sequence>
            <xsd:element name="Valores" type="tcValores" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="ItemListaServico" type="tsItemListaServico" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="CodigoCnae" type="tsCodigoCnae" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="CodigoTributacaoMunicipio" type="tsCodigoTributacao" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="Discriminacao" type="tsDiscriminacao" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="CodigoMunicipio" type="tsCodigoMunicipioIbge" minOccurs="1" maxOccurs="1"/>
    </xsd:sequence>
    """
    
    valores: Valores

    item_lista_servico: str
    """
    Consultar nfse/rj/rio_de_janeiro/manuais/TabelaServicos.txt
    Exemplo:
       item_lista_servico="0101" ->  Analise e desenvolvimento de sistemas.
    """
    discriminacao: str
    """
    Texto livre que descreve o serviço prestado. Máximo de 2000 caracteres.
    """

    codigo_municipio: int
    """
    Código do município de acordo com a tabela do IBGE.

    """

    codigo_tributacao_municipio: str
    """
    Consultar nfse/rj/rio_de_janeiro/manuais/TabelaServicos.txt
    Exemplo:
       item_lista_servico="010104" ->  Geracao de programa de computador sob encomenda.
    """


    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de DadosServico a partir de um elemento XML.
        """
        return cls(
            valores=Valores.from_xml(find_element(xml, 'Valores')),
            item_lista_servico=find_text(xml, 'ItemListaServico', ''),
            codigo_tributacao_municipio=find_text(xml, 'CodigoTributacaoMunicipio', ''),
            discriminacao=find_text(xml, 'Discriminacao', ''),
            codigo_municipio=int(find_text(xml, 'CodigoMunicipio')),
        ) 
    

@dataclass
class IdentificacaoRps:
    """
    <xsd:complexType name="tcIdentificacaoRps">
        <xsd:sequence>
            <xsd:element name="Numero" type="tsNumeroRps" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="Serie" type="tsSerieRps" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="Tipo" type="tsTipoRps" minOccurs="1" maxOccurs="1"/>
        </xsd:sequence>
    </xsd:complexType>
    """

    numero: str
    """
    Número do RPS. Deve ser um número único para cada RPS emitido.
    """

    serie: str
    """
    Série do RPS. Pode ser uma letra ou combinação de letras e números.
    """

    tipo: TipoRps
    """
    Tipo do RPS, conforme a enumeração TipoRps.
    """

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de IdentificacaoRps a partir de um elemento XML.
        """
        return cls(
            numero=find_text(xml, 'Numero', ''),
            serie=find_text(xml, 'Serie', ''),
            tipo= TipoRps(find_text(xml, 'Tipo', '1')),
        )
    
class StatusRps(Enum):
    """
    Código de status do RPS.
    """

    normal = '1'
    cancelado = '2'    

class RegimeEspecialTributacao(Enum):
    """
    Regime especial de tributação.
    -    1 - Microempresa Municipal
    -    2 - Estimativa
    -    3 - Sociedade de Profissionais
    -    4 - Cooperativa
    -    5 - Microempresário Individual
    -    6 - Microempresário e Empresa de Pequeno Porte
    """
    microempresa_municipal = '1'
    estimativa = '2'
    sociedade_de_profissionais = '3'
    cooperativa = '4'
    microempresario_individual = '5'
    microempresario_e_empresa_de_pequeno_porte = '6'


class NaturezaOperacao(Enum):
    """
    Código de natureza da operação.
    -    1 - Tributação no município
    -    2 - Tributação fora do município
    -    3 - Isenção
    -    4 - Imune
    -    5 - Exigibilidade suspensa por decisão judicial
    -    6 - Exigibilidade suspensa por procedimento administrativo
    """
    tributacao_no_municipio = '1'
    tributacao_fora_do_municipio = '2'
    isencao = '3'
    imune = '4'
    exigibilidade_suspensa_por_decisao_judicial = '5'
    exigibilidade_suspensa_por_procedimento_administrativo = '6'



class SituacaoLoteRps(Enum):
    """
    Situação do lote de RPS.
    -    1 - Não Recebido
    -    2 - Não Processado  
    -    3 - Processado com Erro
    -    4 - Processado com Sucesso
    """
    nao_recebido = '1'
    nao_processado = '2'
    processado_com_erro = '3'
    processado_com_sucesso = '4'
    

    @classmethod
    def from_value(cls, value: str) -> 'SituacaoLoteRps':
        """
        Cria uma instância de SituacaoLoteRps a partir do valor string.
        """
        for situacao in cls:
            if situacao.value == str(value):
                return situacao
        raise ValueError(f"Valor inválido para SituacaoLoteRps: {value}")
    

@dataclass
class Endereco:
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    bairro: Optional[str] = None
    codigo_municipio: Optional[str] = None
    """
    abstra_notas/validacoes/cidades/municipios.json

    Busque pela cidade e utilize o campo "id"
    """
    uf: Optional[str] = None
    cep: Optional[str] = None
    complemento: Optional[str] = None

    def __post_init__(self):
        """
        Normaliza o campo UF.
        """
        if self.uf:
            self.uf = normalizar_uf(self.uf)
        if self.cep:
            self.cep = normalizar_cep(self.cep)

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de Endereco a partir de um elemento XML.
        """

        return cls(
            logradouro=find_text(xml, 'Endereco', ''),
            numero=find_text(xml, 'Numero', ''),
            complemento=find_text(xml, 'Complemento', ''),
            bairro=find_text(xml, 'Bairro', ''),
            codigo_municipio=find_text(xml, 'CodigoMunicipio', ''),
            uf = find_text(xml, 'Uf', ''),
            cep=find_text(xml, 'Cep', ''),
        )
    
@dataclass
class Contato:
    """
    <xsd:complexType name="tcContato">
        <xsd:sequence>
            <xsd:element name="Telefone" type="tsTelefone" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="Email" type="tsEmail" minOccurs="0" maxOccurs="1"/>
        </xsd:sequence>
    </xsd:complexType>
    """    
    
    telefone: Optional[str] = None
    email: Optional[str] = None

    def __post_init__(self):
        """
        Normaliza e valida os campos de telefone e email.
        """
        if self.telefone:
            self.telefone = normalizar_validar_telefone(self.telefone)
        if self.email:
            validar_email(self.email)

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de Contato a partir de um elemento XML.
        """
        return cls(
            telefone=find_text(xml, 'Telefone', ''),
            email=find_text(xml, 'Email', ''),
        )
    

@dataclass
class DadosPrestador:
    """
    <xsd:sequence>
            <xsd:element name="IdentificacaoPrestador" type="tcIdentificacaoPrestador" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="RazaoSocial" type="tsRazaoSocial" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="NomeFantasia" type="tsNomeFantasia" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="Endereco" type="tcEndereco" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="Contato" type="tcContato" minOccurs="0" maxOccurs="1"/>
        </xsd:sequence>
    """

    cnpj: str
    razao_social: str
    endereco: Endereco
    inscricao_municipal: Optional[str] = None
    """
    Inscrição municipal do prestador de serviços. Pode ser omitida se o CNPJ for suficiente.
    """
    nome_fantasia: Optional[str] = None
    contato: Optional[Contato] = None

    def __post_init__(self):
        """
        Normaliza o CNPJ e a inscrição municipal.
        """
        self.cnpj = normalizar_cnpj(self.cnpj)
        if self.inscricao_municipal:
            self.inscricao_municipal = normalizar_inscricao_municipal(self.inscricao_municipal)

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de DadosPrestador a partir de um elemento XML.
        """
        identificacao = find_element(xml, 'IdentificacaoPrestador')
        return cls(
            cnpj=find_text(identificacao, 'Cnpj', '') if identificacao is not None else '',
            inscricao_municipal=find_text(identificacao, 'InscricaoMunicipal', '') if identificacao is not None else '',
            razao_social=find_text(xml, 'RazaoSocial', ''),
            nome_fantasia=find_text(xml, 'NomeFantasia', ''),
            endereco=Endereco.from_xml(find_element(xml, 'Endereco')),
            contato=Contato.from_xml(find_element(xml, 'Contato')) if find_element(xml, 'Contato') is not None else None,
        )


@dataclass
class DadosTomador:
    """
    <xsd:complexType name="tcIdentificacaoTomador">
        <xsd:sequence>
            <xsd:element name="CpfCnpj" type="tcCpfCnpj" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="InscricaoMunicipal" type="tsInscricaoMunicipal" minOccurs="0" maxOccurs="1"/>
        </xsd:sequence>
    </xsd:complexType>
    <xsd:complexType name="tcDadosTomador">
        <xsd:sequence>
            <xsd:element name="IdentificacaoTomador" type="tcIdentificacaoTomador" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="RazaoSocial" type="tsRazaoSocial" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="Endereco" type="tcEndereco" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="Contato" type="tcContato" minOccurs="0" maxOccurs="1"/>
        </xsd:sequence>
    </xsd:complexType>
    """

    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    razao_social: Optional[str] = None
    endereco: Optional[Endereco] = None
    contato: Optional[Contato] = None

    def __post_init__(self):
        """
        Normaliza os campos CNPJ e CPF.
        """
        if self.cnpj:
            self.cnpj = normalizar_cnpj(self.cnpj)
        if self.cpf:
            self.cpf = normalizar_cpf(self.cpf)

        assert self.cnpj is None or self.endereco is not None, "Se 'tomador_cnpj' for preenchido, 'tomador_endereco' também deve ser preenchido."
   
    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de DadosTomador a partir de um elemento XML.
        """

        cpf_cnpj_element = find_element(xml, 'CpfCnpj')

        if cpf_cnpj_element is not None:
            cnpj = find_text(cpf_cnpj_element, 'Cnpj', None)
            cpf = find_text(cpf_cnpj_element, 'Cpf', None)
        else:
            cnpj = None
            cpf = None
        return cls(
            cnpj=cnpj,
            cpf=cpf,
            razao_social=find_text(xml, 'RazaoSocial', ''),
            endereco=Endereco.from_xml(find_element(xml, 'Endereco')) if find_element(xml, 'Endereco') is not None else None,
            contato=Contato.from_xml(find_element(xml, 'Contato')) if find_element(xml, 'Contato') is not None else None,
        )
    
@dataclass
class IdentificacaoIntermediarioServico:
    """
    <xsd:complexType name="tcIdentificacaoIntermediarioServico">
    <xsd:sequence>
        <xsd:element name="RazaoSocial" type="tsRazaoSocial" minOccurs="1" maxOccurs="1"/>
        <xsd:element name="CpfCnpj" type="tcCpfCnpj" minOccurs="1" maxOccurs="1"/>
        <xsd:element name="InscricaoMunicipal" type="tsInscricaoMunicipal" minOccurs="0" maxOccurs="1"/>
    </xsd:sequence>
    </xsd:complexType>
    """

    razao_social: str
    cnpj: Optional[str] = None
    cpf: Optional[str] = None
    inscricao_municipal: Optional[str] = None

    def __post_init__(self):
        """
        Normaliza os campos CNPJ e CPF.
        """
        if self.cnpj:
            self.cnpj = normalizar_cnpj(self.cnpj)
        if self.cpf:
            self.cpf = normalizar_cpf(self.cpf)
        
        assert self.cnpj or self.cpf, "CNPJ ou CPF deve ser fornecido."

        if self.inscricao_municipal:
            self.inscricao_municipal = normalizar_inscricao_municipal(self.inscricao_municipal)

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de IdentificacaoIntermediarioServico a partir de um elemento XML.
        """

        if find_element(xml, 'CpfCnpj'):
            cnpj = find_text(find_element(xml, 'CpfCnpj'), 'Cnpj', None)
            cpf = find_text(find_element(xml, 'CpfCnpj'), 'Cpf', None)
        else:
            cnpj = None
            cpf = None

        return cls(
            razao_social=find_text(xml, 'RazaoSocial', ''),
            cnpj=cnpj,
            cpf=cpf,
            inscricao_municipal=find_text(xml, 'InscricaoMunicipal', None),
        )
    
@dataclass
class IdentificacaoOrgaoGerador:
    """
    <xsd:complexType name="tcIdentificacaoOrgaoGerador">
        <xsd:sequence>
            <xsd:element name="CodigoMunicipio" type="tsCodigoMunicipioIbge" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="Uf" type="tsUf" minOccurs="1" maxOccurs="1"/>
        </xsd:sequence>
    </xsd:complexType>
    """

    codigo_municipio: str
    uf: str

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de IdentificacaoOrgaoGerador a partir de um elemento XML.
        """
        return cls(
            codigo_municipio=find_text(xml, 'CodigoMunicipio', ''),
            uf=find_text(xml, 'Uf', ''),
        )
    
@dataclass
class DadosConstrucaoCivil:
    """
    <xsd:complexType name="tcDadosConstrucaoCivil">
        <xsd:sequence>
            <xsd:element name="CodigoObra" type="tsCodigoObra" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="Art" type="tsArt" minOccurs="1" maxOccurs="1"/>
        </xsd:sequence>
    </xsd:complexType>
    """

    codigo_obra: str
    art: Optional[str] = None

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de DadosConstrucaoCivil a partir de um elemento XML.
        """
        return cls(
            codigo_obra=find_text(xml, 'CodigoObra', ''),
            art=find_text(xml, 'Art', None),
        )
    
@dataclass
class Nfse:
    """
    <xsd:complexType name="tcInfNfse">
        <xsd:sequence>
            <xsd:element name="Numero" type="tsNumeroNfse" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="CodigoVerificacao" type="tsCodigoVerificacao" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="DataEmissao" type="xsd:dateTime" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="IdentificacaoRps" minOccurs="0" type="tcIdentificacaoRps" maxOccurs="1"/>
            <xsd:element name="DataEmissaoRps" type="xsd:date" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="NaturezaOperacao" type="tsNaturezaOperacao" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="RegimeEspecialTributacao" type="tsRegimeEspecialTributacao" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="OptanteSimplesNacional" type="tsSimNao" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="IncentivadorCultural" type="tsSimNao" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="Competencia" type="xsd:dateTime" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="NfseSubstituida" type="tsNumeroNfse" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="OutrasInformacoes" type="tsOutrasInformacoes" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="Servico" type="tcDadosServico" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="ValorCredito" type="tsValor" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="PrestadorServico" type="tcDadosPrestador" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="TomadorServico" type="tcDadosTomador" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="IntermediarioServico" type="tcIdentificacaoIntermediarioServico" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="OrgaoGerador" type="tcIdentificacaoOrgaoGerador" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="ConstrucaoCivil" type="tcDadosConstrucaoCivil" minOccurs="0" maxOccurs="1"/>
        </xsd:sequence>
        <xsd:attribute name="Id" type="tsIdTag" />
    </xsd:complexType>
    """
    numero: str
    codigo_verificacao: str
    data_emissao: datetime
    identificacao_rps: Optional[IdentificacaoRps]
    data_emissao_rps: Optional[datetime]
    natureza_operacao: Optional[NaturezaOperacao]
    regime_especial_tributacao: Optional[RegimeEspecialTributacao]
    optante_simples_nacional: Optional[bool]
    incentivador_cultural: Optional[bool]
    competencia: Optional[datetime]
    nfse_substituida: Optional[str]
    outras_informacoes: Optional[str]
    servico: Optional[DadosServico]
    valor_credito_centavos: Optional[int]
    prestador_servico: Optional[DadosPrestador]
    tomador_servico: Optional[DadosTomador]
    intermediario_servico: Optional[IdentificacaoIntermediarioServico]
    orgao_gerador: Optional[IdentificacaoOrgaoGerador]
    construcao_civil: Optional[DadosConstrucaoCivil]

    def __post_init__(self):
        self.data_emissao = normalizar_data(self.data_emissao)

    @property
    def optante_simples_nacional_str(self):
        """
        Retorna 'S' se for optante do Simples Nacional, 'N' caso contrário.
        """
        return '1' if self.optante_simples_nacional else '2'
    
    @property
    def incentivador_cultural_str(self):
        """
        Retorna 'S' se for incentivador cultural, 'N' caso contrário.
        """
        return '1' if self.incentivador_cultural else '2'
    
    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de Nfse a partir de um elemento XML.
        """

        return cls(
            numero=find_text(xml, 'Numero', ''),
            codigo_verificacao=find_text(xml, 'CodigoVerificacao', ''),
            data_emissao=datetime.fromisoformat(find_text(xml, 'DataEmissao', '')),
            identificacao_rps=IdentificacaoRps.from_xml(find_element(xml, 'IdentificacaoRps')) if find_element(xml, 'IdentificacaoRps') is not None else None,
            data_emissao_rps=datetime.fromisoformat(find_text(xml, 'DataEmissaoRps', '')) if find_element(xml, 'DataEmissaoRps') is not None else None,
            natureza_operacao=NaturezaOperacao(find_text(xml, 'NaturezaOperacao', '')) if find_element(xml, 'NaturezaOperacao') is not None else None,
            regime_especial_tributacao=RegimeEspecialTributacao(find_text(xml, 'RegimeEspecialTributacao', '')) if find_element(xml, 'RegimeEspecialTributacao') is not None else None,
            optante_simples_nacional=find_text(xml, 'OptanteSimplesNacional', 'N') == 'S',
            incentivador_cultural=find_text(xml, 'IncentivadorCultural', 'N') == 'S',
            competencia=datetime.fromisoformat(find_text(xml, 'Competencia', '')) if find_element(xml, 'Competencia') is not None else None,
            nfse_substituida=find_text(xml, 'NfseSubstituida', None),
            outras_informacoes=find_text(xml, 'OutrasInformacoes', None),
            servico=DadosServico.from_xml(find_element(xml, 'Servico')) if find_element(xml, 'Servico') is not None else None,
            valor_credito_centavos=int(float(find_text(xml, 'ValorCredito', '0')) * 100) if find_element(xml, 'ValorCredito') is not None else None,
            prestador_servico=DadosPrestador.from_xml(find_element(xml, 'PrestadorServico')) if find_element(xml, 'PrestadorServico') is not None else None,
            tomador_servico=DadosTomador.from_xml(find_element(xml, 'TomadorServico')) if find_element(xml, 'TomadorServico') is not None else None,
            intermediario_servico=IdentificacaoIntermediarioServico.from_xml(find_element(xml, 'IntermediarioServico')) if find_element(xml, 'IntermediarioServico') is not None else None,
            orgao_gerador=IdentificacaoOrgaoGerador.from_xml(find_element(xml, 'OrgaoGerador')) if find_element(xml, 'OrgaoGerador') is not None else None,
            construcao_civil=DadosConstrucaoCivil.from_xml(find_element(xml, 'ConstrucaoCivil')) if find_element(xml, 'ConstrucaoCivil') is not None else None,
        )
    
@dataclass
class IdentificacaoNfse:
    """
    <xsd:complexType name="tcIdentificacaoNfse">
        <xsd:sequence>
            <xsd:element name="Numero" type="tsNumeroNfse" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="Cnpj" type="tsCnpj" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="InscricaoMunicipal" type="tsInscricaoMunicipal" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="CodigoMunicipio" type="tsCodigoMunicipioIbge" minOccurs="1" maxOccurs="1"/>
        </xsd:sequence>
    """

    numero: str
    cnpj: str
    codigo_municipio: str
    inscricao_municipal: Optional[str] = None

    def __post_init__(self):
        """
        Normaliza o CNPJ e a inscrição municipal.
        """
        self.cnpj = normalizar_cnpj(self.cnpj)
        if self.inscricao_municipal:
            self.inscricao_municipal = normalizar_inscricao_municipal(self.inscricao_municipal)

        assert self.cnpj, "CNPJ deve ser fornecido."
        assert self.codigo_municipio, "Código do município deve ser fornecido."

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de IdentificacaoNfse a partir de um elemento XML.
        """
        return cls(
            numero=find_text(xml, 'Numero', ''),
            cnpj=find_text(xml, 'Cnpj', ''),
            inscricao_municipal=find_text(xml, 'InscricaoMunicipal', ''),
            codigo_municipio=find_text(xml, 'CodigoMunicipio', ''),
        )


@dataclass
class PedidoCancelamento:
    """
    <xsd:complexType name="tcInfPedidoCancelamento">
        <xsd:sequence>
            <xsd:element name="IdentificacaoNfse" type="tcIdentificacaoNfse" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="CodigoCancelamento" type="tsCodigoCancelamentoNfse" minOccurs="0" maxOccurs="1"/>
        </xsd:sequence>
        <xsd:attribute name="Id" type="tsIdTag" />
    </xsd:complexType>
    """

    id: str
    identificacao_nfse: IdentificacaoNfse
    codigo_cancelamento: Optional[str] = None

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de PedidoCancelamento a partir de um elemento XML.
        """
        return cls(
            id=xml.get('Id', ''),
            identificacao_nfse=IdentificacaoNfse.from_xml(find_element(xml, 'IdentificacaoNfse')) if find_element(xml, 'IdentificacaoNfse') is not None else None,
            codigo_cancelamento=find_text(xml, 'CodigoCancelamento', None),
        )
    
@dataclass
class ConfirmacaoCancelamento:
    """
    <xsd:complexType name="tcConfirmacaoCancelamento">
        <xsd:sequence>
            <xsd:element name="Pedido" type="tcPedidoCancelamento" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="DataHoraCancelamento" type="xsd:dateTime" minOccurs="1" maxOccurs="1"/>
        </xsd:sequence>
        <xsd:attribute name="Id" type="tsIdTag" />
    </xsd:complexType>
    """
    
    id: str
    pedido: PedidoCancelamento
    data_hora_cancelamento: datetime

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de ConfirmacaoCancelamento a partir de um elemento XML.
        """
        return cls(
            id=xml.get('Id', ''),
            pedido=PedidoCancelamento.from_xml(find_element(xml, 'Pedido')) if find_element(xml, 'Pedido') is not None else None,
            data_hora_cancelamento=datetime.fromisoformat(find_text(xml, 'DataHoraCancelamento', '')),
        )
    

@dataclass
class SubstituicaoNfse:
    """
    <xsd:complexType name="tcInfSubstituicaoNfse">
        <xsd:sequence>
            <xsd:element name="NfseSubstituidora" type="tsNumeroNfse" minOccurs="1" maxOccurs="1"/>
        </xsd:sequence>
        <xsd:attribute name="Id" type="tsIdTag"/>
    </xsd:complexType>
    """
    
    id: str
    nfse_substituidora: str

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de SubstituicaoNfse a partir de um elemento XML.
        """
        return cls(
            id=xml.get('Id', ''),
            nfse_substituidora=find_text(xml, 'NfseSubstituidora', ''),
        )
    
@dataclass
class CompNfse:
    """
    <xsd:complexType name="tcCompNfse">
        <xsd:sequence>
            <xsd:element name="Nfse" type="tcNfse" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="NfseCancelamento" type="tcCancelamentoNfse" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="NfseSubstituicao" type="tcSubstituicaoNfse" minOccurs="0" maxOccurs="1"/>
        </xsd:sequence>
    </xsd:complexType>
    """
    
    nfse: Nfse
    nfse_cancelamento: Optional[ConfirmacaoCancelamento] = None
    nfse_substituicao: Optional[SubstituicaoNfse] = None

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de CompNfse a partir de um elemento XML.
        """
        return cls(
            nfse=Nfse.from_xml(find_element(xml, 'Nfse')),
            nfse_cancelamento=ConfirmacaoCancelamento.from_xml(find_element(xml, 'NfseCancelamento')) if find_element(xml, 'NfseCancelamento') is not None else None,
            nfse_substituicao=SubstituicaoNfse.from_xml(find_element(xml, 'NfseSubstituicao')) if find_element(xml, 'NfseSubstituicao') is not None else None,
        )
    
@dataclass
class Rps:
    """
    <xsd:complexType name="tcInfRps">
        <xsd:sequence>
            <xsd:element name="IdentificacaoRps" type="tcIdentificacaoRps" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="DataEmissao" type="xsd:dateTime" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="NaturezaOperacao" type="tsNaturezaOperacao" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="RegimeEspecialTributacao" type="tsRegimeEspecialTributacao" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="OptanteSimplesNacional" type="tsSimNao" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="IncentivadorCultural" type="tsSimNao" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="Status" type="tsStatusRps" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="RpsSubstituido" type="tcIdentificacaoRps" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="Servico" type="tcDadosServico" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="Prestador" type="tcIdentificacaoPrestador" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="Tomador" type="tcDadosTomador" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="IntermediarioServico" type="tcIdentificacaoIntermediarioServico" minOccurs="0" maxOccurs="1"/>
            <xsd:element name="ConstrucaoCivil" type="tcDadosConstrucaoCivil" minOccurs="0" maxOccurs="1"/>
        </xsd:sequence>
        <xsd:attribute name="Id" type="tsIdTag" />
    </xsd:complexType>
    """

    id: str
    identificacao_rps: IdentificacaoRps
    data_emissao: datetime
    natureza_operacao: NaturezaOperacao
    optante_simples_nacional: bool
    incentivador_cultural: bool
    status: StatusRps
    servico: DadosServico
    prestador_cnpj: str
    prestador_inscricao_municipal: Optional[str] = None
    regime_especial_tributacao: Optional[RegimeEspecialTributacao] = None
    rps_substituido: Optional[IdentificacaoRps] = None
    tomador: Optional[DadosTomador] = None
    intermediario_servico: Optional[IdentificacaoIntermediarioServico] = None
    construcao_civil: Optional[DadosConstrucaoCivil] = None

    @property
    def optante_simples_nacional_str(self):
        """
        Retorna 'S' se for optante do Simples Nacional, 'N' caso contrário.
        """
        return '1' if self.optante_simples_nacional else '2'

    @property
    def incentivador_cultural_str(self):
        """
        Retorna 'S' se for incentivador cultural, 'N' caso contrário.
        """
        return '1' if self.incentivador_cultural else '2'
    
    @property
    def data_emissao_iso8601(self):
        """
        Retorna a data de emissão no formato ISO 8601.
        """
        return self.data_emissao.isoformat()

    def __post_init__(self):
        """
        Valida os dados após a inicialização da classe.
        """
        self.prestador_cnpj = normalizar_cnpj(self.prestador_cnpj)
        if self.prestador_inscricao_municipal:
            self.prestador_inscricao_municipal = normalizar_inscricao_municipal(self.prestador_inscricao_municipal)


    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de Rps a partir de um elemento XML.
        """
        return cls(
            id=xml.get('Id', ''),
            identificacao_rps=IdentificacaoRps.from_xml(find_element(xml, 'IdentificacaoRps')),
            data_emissao=datetime.fromisoformat(find_text(xml, 'DataEmissao', '')),
            natureza_operacao=NaturezaOperacao(find_text(xml, 'NaturezaOperacao', '')) if find_element(xml, 'NaturezaOperacao') is not None else None,
            regime_especial_tributacao=RegimeEspecialTributacao(find_text(xml, 'RegimeEspecialTributacao', '')) if find_element(xml, 'RegimeEspecialTributacao') is not None else None,
            optante_simples_nacional=find_text(xml, 'OptanteSimplesNacional', 'N') == 'S',
            incentivador_cultural=find_text(xml, 'IncentivadorCultural', 'N') == 'S',
            status=StatusRps.from_value(find_text(xml, 'Status', '1')),
            rps_substituido=IdentificacaoRps.from_xml(find_element(xml, 'RpsSubstituido')) if find_element(xml, 'RpsSubstituido') is not None else None,
            servico=DadosServico.from_xml(find_element(xml, 'Servico')),
            prestador_cnpj=normalizar_cnpj(find_text(xml, 'Prestador/Cnpj', '')),
            prestador_inscricao_municipal=find_text(xml, 'Prestador/InscricaoMunicipal', ''),
            tomador=DadosTomador.from_xml(find_element(xml, 'Tomador')) if find_element(xml, 'Tomador') is not None else None,
            intermediario_servico=IdentificacaoIntermediarioServico.from_xml(find_element(xml, 'IntermediarioServico')) if find_element(xml, 'IntermediarioServico') is not None else None,
            construcao_civil=DadosConstrucaoCivil.from_xml(find_element(xml, 'ConstrucaoCivil')) if find_element(xml, 'ConstrucaoCivil') is not None else None,
        )


@dataclass
class MensagemRetorno:
    """
    <xsd:sequence>
            <xsd:element name="Codigo" type="tsCodigoMensagemAlerta" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="Mensagem" type="tsDescricaoMensagemAlerta" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="Correcao" type="tsDescricaoMensagemAlerta" minOccurs="0"/>
    </xsd:sequence>
    """

    codigo: str
    """
    Código da mensagem de retorno.
    """

    mensagem: str
    """
    Texto da mensagem de retorno.
    """

    correcao: Optional[str] = None
    """
    Texto opcional com a correção sugerida para o erro, se aplicável.
    """

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de MensagemRetorno a partir de um elemento XML.
        """
        return cls(
            codigo=find_text(xml, 'Codigo', ''),
            mensagem=find_text(xml, 'Mensagem', ''),
            correcao=find_text(xml, 'Correcao', None),
        )
    
@dataclass
class MensagemRetornoLote:
    """
    <xsd:sequence>
            <xsd:element name="IdentificacaoRps" type="tcIdentificacaoRps" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="Codigo" type="tsCodigoMensagemAlerta" minOccurs="1" maxOccurs="1"/>
            <xsd:element name="Mensagem" type="tsDescricaoMensagemAlerta" minOccurs="1" maxOccurs="1"/>
    </xsd:sequence>
    """
    
    identificacao_rps: IdentificacaoRps
    """
    Identificação do RPS relacionado à mensagem de retorno.
    """

    codigo: str
    """
    Código da mensagem de retorno.
    """

    mensagem: str
    """
    Texto da mensagem de retorno.
    """

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de MensagemRetornoLote a partir de um elemento XML.
        """
        return cls(
            identificacao_rps=IdentificacaoRps.from_xml(find_element(xml, 'IdentificacaoRps')),
            codigo=find_text(xml, 'Codigo', ''),
            mensagem=find_text(xml, 'Mensagem', ''),
        )
    

# Consultar Nfse
@dataclass
class ConsultarNfseResposta:
    """
    <xsd:element name="ConsultarNfseRpsResposta">
        <xsd:complexType>
            <xsd:choice>
                <xsd:element name="CompNfse" type="tcCompNfse" minOccurs="1" maxOccurs="1"/>
                <xsd:element ref="ListaMensagemRetorno" minOccurs="1" maxOccurs="1"/>
            </xsd:choice>
        </xsd:complexType>
    </xsd:element>
    """
    comp_nfse: CompNfse
    lista_mensagem_retorno: Optional[List[MensagemRetorno]] = None

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de ConsultarNfseResposta a partir de um elemento XML.
        """

        if find_element(xml, 'ListaMensagemRetorno') is not None:
            mensagens = find_all_elements(xml, 'MensagemRetorno')
            lista_mensagem_retorno = [MensagemRetorno.from_xml(m) for m in mensagens]
            return cls(
                comp_nfse=None,
                lista_mensagem_retorno=lista_mensagem_retorno
            )
        else:
            lista_nfse = find_element(xml, 'ListaNfse')
            if lista_nfse is not None:
                comp_nfses = find_all_elements(lista_nfse, 'CompNfse')
                comp_nfse_list = [CompNfse.from_xml(comp) for comp in comp_nfses]
            
            else:
                comp_nfse_element = find_element(xml, 'CompNfse')
                if comp_nfse_element is not None:
                    comp_nfse_list = [CompNfse.from_xml(comp_nfse_element)]
                else:
                    comp_nfse_list = []
            
            return cls(
                comp_nfse=comp_nfse_list if comp_nfse_list else None,
                lista_mensagem_retorno=None
            )
        
@dataclass
class ConsultarNfseEnvio(Envio[ConsultarNfseResposta]):
    """
    Classe para consultar Nfse via período de emissão, número da nota, tomador ou intermediário.
    """
    prestador_cnpj: str
    prestador_inscricao_municipal: Optional[str] = None
    data_inicial: Optional[datetime] = None
    data_final: Optional[datetime] = None
    numero_nfse: Optional[str] = None

    tomador_cpf: Optional[str] = None
    tomador_cnpj: Optional[str] = None
    tomador_inscricao_municipal: Optional[str] = None

    intermediario_servico: Optional[IdentificacaoIntermediarioServico] = None


    def __post_init__(self):
        """
        Normaliza o CNPJ do prestador e a inscrição municipal.
        """
        self.prestador_cnpj = normalizar_cnpj(self.prestador_cnpj)
        if self.prestador_inscricao_municipal:
            self.prestador_inscricao_municipal = normalizar_inscricao_municipal(self.prestador_inscricao_municipal)

        if self.tomador_cnpj:
            self.tomador_cnpj = normalizar_cnpj(self.tomador_cnpj)
        if self.tomador_cpf:
            self.tomador_cpf = normalizar_cpf(self.tomador_cpf)
        
        if self.tomador_inscricao_municipal:
            self.tomador_inscricao_municipal = normalizar_inscricao_municipal(self.tomador_inscricao_municipal)
        
        if self.data_inicial:
            self.data_inicial = normalizar_data(self.data_inicial)
        if self.data_final:
            self.data_final = normalizar_data(self.data_final)
    
    def nome_operacao(self):
        return "ConsultarNfse"
    
    def resposta(self, xml):
        return ConsultarNfseResposta.from_xml(xml)
    

@dataclass
class ConsultarNfsePorRpsResposta:
    """ 
    <xsd:element name="ConsultarNfseRpsResposta">
        <xsd:complexType>
            <xsd:choice>
                <xsd:element name="CompNfse" type="tcCompNfse" minOccurs="1" maxOccurs="1"/>
                <xsd:element ref="ListaMensagemRetorno" minOccurs="1" maxOccurs="1"/>
            </xsd:choice>
        </xsd:complexType>
    </xsd:element>
    """
    comp_nfse: CompNfse
    lista_mensagem_retorno: Optional[List[MensagemRetorno]] = None

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de ConsultarNfsePorRpsResposta a partir de um elemento XML.
        """
        if find_element(xml, 'ListaMensagemRetorno') is not None:
            mensagens = find_all_elements(xml, 'MensagemRetorno')
            lista_mensagem_retorno = [MensagemRetorno.from_xml(m) for m in mensagens]
            return cls(
                comp_nfse=None,
                lista_mensagem_retorno=lista_mensagem_retorno
            )
        else:
            comp_nfse_element = find_element(xml, 'CompNfse')
            if comp_nfse_element is not None:
                comp_nfse = CompNfse.from_xml(comp_nfse_element)
                return cls(
                    comp_nfse=comp_nfse,
                    lista_mensagem_retorno=None
                )
            else:
                return cls(
                    comp_nfse=None,
                    lista_mensagem_retorno=None
                )
            
@dataclass
class ConsultarNfsePorRpsEnvio(Envio[ConsultarNfsePorRpsResposta]):
    """
    Classe para consultar Nfse por RPS.

     <xsd:element name="ConsultarNfseRpsEnvio">
        <xsd:complexType>
            <xsd:sequence>
                <xsd:element name="IdentificacaoRps" type="tcIdentificacaoRps" minOccurs="1" maxOccurs="1"/>
                <xsd:element name="Prestador" type="tcIdentificacaoRps" minOccurs="1" maxOccurs="1"/>
            </xsd:sequence>
        </xsd:complexType>
    </xsd:element>
    """
    identificacao_rps: IdentificacaoRps
    prestador_cnpj: str
    prestador_inscricao_municipal: Optional[str] = None

    def __post_init__(self):
        """
        Normaliza o CNPJ do prestador.
        """
        self.prestador_cnpj = normalizar_cnpj(self.prestador_cnpj)
        if self.prestador_inscricao_municipal:
            self.prestador_inscricao_municipal = normalizar_inscricao_municipal(self.prestador_inscricao_municipal)
    
    def nome_operacao(self):
        return "ConsultarNfsePorRps"
    
    def resposta(self, xml):
        return ConsultarNfsePorRpsResposta.from_xml(xml)
    

@dataclass
class GerarNfseResposta:
    """
    <xsd:element name="GerarNfseResposta">
    <xsd:complexType>
      <xsd:choice>
        <xsd:sequence>
          <xsd:element ref="CompNfse" minOccurs="1" maxOccurs="1" />
          <xsd:element ref="ListaMensagemRetorno"  minOccurs="0" maxOccurs="1"/>
        </xsd:sequence>
        <xsd:element ref="ListaMensagemRetorno" minOccurs="1" maxOccurs="1" />
      </xsd:choice>
    </xsd:complexType>
  </xsd:element>
  """
    comp_nfse: CompNfse
    lista_mensagem_retorno: Optional[List[MensagemRetorno]] = None

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de GerarNfseResposta a partir de um elemento XML.
        """
        if find_element(xml, 'ListaMensagemRetorno') is not None:
            mensagens = find_all_elements(xml, 'MensagemRetorno')
            lista_mensagem_retorno = [MensagemRetorno.from_xml(m) for m in mensagens]
            return cls(
                comp_nfse=None,
                lista_mensagem_retorno=lista_mensagem_retorno
            )
        else:
            comp_nfse_element = find_element(xml, 'CompNfse')
            if comp_nfse_element is not None:
                comp_nfse = CompNfse.from_xml(comp_nfse_element)
                return cls(
                    comp_nfse=comp_nfse,
                    lista_mensagem_retorno=None
                )
            else:
                return cls(
                    comp_nfse=None,
                    lista_mensagem_retorno=None
                )
    


    
@dataclass
class GerarNfseEnvio(Envio[GerarNfseResposta]):
    """
  <xsd:element name="GerarNfseEnvio">
    <xsd:complexType>
      <xsd:sequence>
        <xsd:element name="Rps" type="tcRps" minOccurs="1" maxOccurs="1" />
      </xsd:sequence>
    </xsd:complexType>
  </xsd:element>
    """
  
    rps: Rps
    
    def nome_operacao(self):
        return "GerarNfse"
    
    def resposta(self, xml):
        return GerarNfseResposta.from_xml(xml)


@dataclass
class EnviarLoteRpsResposta:
    """
    <xsd:sequence>
        <xsd:element name="NumeroLote" type="tsNumeroLote" minOccurs="1" maxOccurs="1"/>
        <xsd:element name="DataRecebimento" type="xsd:dateTime" minOccurs="1" maxOccurs="1"/>
        <xsd:element name="Protocolo" type="tsNumeroProtocolo" minOccurs="1" maxOccurs="1"/>
        <xsd:element ref="ListaMensagemRetorno" minOccurs="1" maxOccurs="1"/>
    </xsd:sequence>
    """
    numero_lote: str
    data_recebimento: datetime
    protocolo: str
    lista_mensagem_retorno: List[MensagemRetorno]

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de EnviarLoteRpsResposta a partir de um elemento XML.
        """
        
        if find_element(xml, 'ListaMensagemRetorno') is not None:
            mensagens = find_all_elements(xml, 'MensagemRetorno')
            lista_mensagem_retorno = [MensagemRetorno.from_xml(m) for m in mensagens]
            return cls(numero_lote=None, data_recebimento=None, protocolo=None, lista_mensagem_retorno=lista_mensagem_retorno)
        
        return cls(
            numero_lote=find_text(xml, 'NumeroLote', ''),
            data_recebimento=datetime.fromisoformat(find_text(xml, 'DataRecebimento', '')),
            protocolo=find_text(xml, 'Protocolo', ''),
            lista_mensagem_retorno=[]
        )
        

@dataclass
class EnviarLoteRpsEnvio(Envio[EnviarLoteRpsResposta]):
    """
    <xsd:sequence>
        <xsd:element name="NumeroLote" type="tsNumeroLote" minOccurs="1" maxOccurs="1"/>
        <xsd:element name="Cnpj" type="tsCnpj" minOccurs="1" maxOccurs="1"/>
        <xsd:element name="InscricaoMunicipal" type="tsInscricaoMunicipal" minOccurs="1" maxOccurs="1"/>
        <xsd:element name="QuantidadeRps" type="tsQuantidadeRps" minOccurs="1" maxOccurs="1"/>
        <xsd:element name="ListaRps" minOccurs="1" maxOccurs="1">
            <xsd:complexType>
                <xsd:sequence>
                    <xsd:element name="Rps" maxOccurs="unbounded" type="tcRps" minOccurs="1">
                    </xsd:element>
                </xsd:sequence>
            </xsd:complexType>
                </xsd:element>
        </xsd:sequence>
        <xsd:attribute name="Id" type="tsIdTag" />
    """
    
    lote_id: str
    numero_lote: str
    prestador_cnpj: str
    prestador_inscricao_municipal: str
    lista_rps: List[Rps]
    quantidade_rps: int = 0

    def __post_init__(self):
        """
        Normaliza o CNPJ do prestador e a inscrição municipal.
        """
        self.prestador_cnpj = normalizar_cnpj(self.prestador_cnpj)
        self.prestador_inscricao_municipal = normalizar_inscricao_municipal(self.prestador_inscricao_municipal)
    
        if not self.lista_rps:
            raise ValueError("A lista de RPS não pode estar vazia.")
        
        self.quantidade_rps = len(self.lista_rps)
        
    def nome_operacao(self):
        return "RecepcionarLoteRps"
    
    def resposta(self, xml: ElementBase) -> EnviarLoteRpsResposta:
        return EnviarLoteRpsResposta.from_xml(xml)


@dataclass
class ConsultarSituacaoLoteRpsResposta:
    """
    <xsd:sequence>
        <xsd:element name="NumeroLote" type="tsNumeroLote" minOccurs="1" maxOccurs="1"/>
        <xsd:element name="Situacao" type="tsSituacaoLoteRps" minOccurs="1" maxOccurs="1"/>
    </xsd:sequence>
    <xsd:element ref="ListaMensagemRetorno" minOccurs="1" maxOccurs="1"/>
    """
    
    numero_lote: str
    situacao: str
    lista_mensagem_retorno: Optional[List[MensagemRetorno]] = None


    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de ConsultarSituacaoLoteRpsResposta a partir de um elemento XML.
        """
        if find_element(xml, 'ListaMensagemRetorno') is not None:
            mensagens = find_all_elements(xml, 'MensagemRetorno')
            lista_mensagem_retorno = [MensagemRetorno.from_xml(m) for m in mensagens]
            return cls(numero_lote=None, situacao=None, lista_mensagem_retorno=lista_mensagem_retorno)
        
        # Converte o código numérico para descrição legível
        situacao_codigo = find_text(xml, 'Situacao', None)
        situacao_descricao = None
        if situacao_codigo:
            try:
                situacao_enum = SituacaoLoteRps.from_value(situacao_codigo)
                situacao_descricao = situacao_enum
            except ValueError:
                situacao_descricao = f"Situação desconhecida: {situacao_codigo}"

        return cls(
            numero_lote=find_text(xml, 'NumeroLote', None),
            situacao=situacao_descricao,
            lista_mensagem_retorno=None
        )

    

@dataclass
class ConsultarSituacaoLoteRpsEnvio(Envio[ConsultarSituacaoLoteRpsResposta]):
    """
    Consultar a situação de um lote de RPS.
    <xsd:sequence>
        <xsd:element name="Prestador" type="tcIdentificacaoPrestador" minOccurs="1" maxOccurs="1"/>
        <xsd:element name="Protocolo" type="tsNumeroProtocolo" minOccurs="1" maxOccurs="1"/>
    </xsd:sequence>
    """
    
    protocolo: str
    prestador_cnpj: str
    prestador_inscricao_municipal: Optional[str] = None

    def __post_init__(self):
        """
        Normaliza o CNPJ do prestador e a inscrição municipal.
        """
        self.prestador_cnpj = normalizar_cnpj(self.prestador_cnpj)
        if self.prestador_inscricao_municipal:
            self.prestador_inscricao_municipal = normalizar_inscricao_municipal(self.prestador_inscricao_municipal)
    
    def nome_operacao(self):
        return "ConsultarSituacaoLoteRps"
    
    def resposta(self, xml: ElementBase) -> ConsultarSituacaoLoteRpsResposta:
        return ConsultarSituacaoLoteRpsResposta.from_xml(xml)
    

@dataclass
class ConsultarLoteRpsResposta:
    """
    Resposta da consulta de lote de RPS.
    <xsd:choice>
        <xsd:element name="ListaNfse" minOccurs="1" maxOccurs="1">
            <xsd:complexType>
                <xsd:sequence>
                    <xsd:element name="CompNfse" maxOccurs="unbounded" type="tcCompNfse" minOccurs="1"/>
                </xsd:sequence>
            </xsd:complexType>
        </xsd:element>
        <xsd:element ref="ListaMensagemRetorno" minOccurs="1" maxOccurs="1"/>
    </xsd:choice>
    """

    comp_nfse: Optional[List[CompNfse]] = None
    lista_mensagem_retorno: Optional[List[MensagemRetorno]] = None

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de ConsultarLoteRpsResposta a partir de um elemento XML.
        """
        if find_element(xml, 'ListaMensagemRetorno') is not None:
            mensagens = find_all_elements(xml, 'MensagemRetorno')
            lista_mensagem_retorno = [MensagemRetorno.from_xml(m) for m in mensagens]
            return cls(comp_nfse=[], lista_mensagem_retorno=lista_mensagem_retorno)
        
        comp_nfse_elements = find_all_elements(xml, 'CompNfse')
        comp_nfse_list = [CompNfse.from_xml(comp) for comp in comp_nfse_elements]

        return cls(comp_nfse=comp_nfse_list, lista_mensagem_retorno=None)
    

@dataclass
class ConsultarLoteRpsEnvio(Envio[ConsultarLoteRpsResposta]):
    """
    Consultar lote de RPS.
    <xsd:sequence>
                <xsd:element name="Prestador" type="tcIdentificacaoPrestador" minOccurs="1" maxOccurs="1"/>
                <xsd:element name="Protocolo" type="tsNumeroProtocolo" minOccurs="1" maxOccurs="1"/>
            </xsd:sequence>
    """
    
    prestador_cnpj: str
    protocolo: str
    prestador_inscricao_municipal: Optional[str] = None
    

    def __post_init__(self):
        """
        Normaliza o CNPJ do prestador e a inscrição municipal.
        """
        self.prestador_cnpj = normalizar_cnpj(self.prestador_cnpj)
        if self.prestador_inscricao_municipal:
            self.prestador_inscricao_municipal = normalizar_inscricao_municipal(self.prestador_inscricao_municipal)
    
    def nome_operacao(self):
        return "ConsultarLoteRps"
    
    def resposta(self, xml: ElementBase) -> ConsultarLoteRpsResposta:
        return ConsultarLoteRpsResposta.from_xml(xml)