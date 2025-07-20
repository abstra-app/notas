from dataclasses import dataclass
from datetime import datetime
from .base import Envio
from abstra_notas.validacoes.cnpj import normalizar_cnpj
from abstra_notas.validacoes.data import normalizar_data
from abstra_notas.validacoes.cpf import normalizar_cpf
from abstra_notas.validacoes.cidades import normalizar_uf
from abstra_notas.validacoes.cep import normalizar_cep
from abstra_notas.validacoes.telefone import normalizar_telefone
from abstra_notas.validacoes.data import normalizar_data
from abstra_notas.validacoes.email import validar_email
from typing import List, Optional
from lxml.etree import ElementBase
from logging import warning
from enum import Enum


def find_element(parent: ElementBase, tag_name: str):
    """
    Busca um elemento ignorando namespace.
    """
    print(f"Buscando elemento: '{tag_name}'")
    # Busca primeiro sem namespace
    element = parent.find(tag_name)
    if element is not None:
        print(f"Encontrado '{tag_name}' sem namespace")
        return element
    
    # Se não encontrou, busca com qualquer namespace usando xpath
    try:
        xpath = f".//*[local-name()='{tag_name}']"
        elements = parent.xpath(xpath)
        if elements:
            print(f"Encontrado '{tag_name}' com XPath")
            return elements[0]
        else:
            print(f"XPath não encontrou '{tag_name}'")
    except Exception as e:
        print(f"Erro no XPath para '{tag_name}': {e}")
        
    # Fallback: busca por todos os filhos e verifica o nome local
    print(f"Usando fallback para '{tag_name}'")
    for elem in parent.iter():
        if elem.tag.split('}')[-1] == tag_name:  # Remove namespace do tag
            print(f"Fallback encontrou '{tag_name}' - tag completa: {elem.tag}")
            return elem
    print(f"Fallback não encontrou '{tag_name}'")
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
            if elem.tag.split('}')[-1] == tag_name:  # Remove namespace do tag
                result.append(elem)
        print(f"Fallback encontrou {len(result)} elementos para '{tag_name}'")
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
    	<xsd:complexType name="tcValores">
		<xsd:sequence>
			<xsd:element name="ValorServicos" type="tsValor"/>
			<xsd:element name="ValorDeducoes" type="tsValor" minOccurs="0"/>
			<xsd:element name="ValorPis" type="tsValor" minOccurs="0"/>
			<xsd:element name="ValorCofins" type="tsValor" minOccurs="0"/>
			<xsd:element name="ValorInss" type="tsValor" minOccurs="0"/>
			<xsd:element name="ValorIr" type="tsValor" minOccurs="0"/>
			<xsd:element name="ValorCsll" type="tsValor" minOccurs="0"/>
			<xsd:element name="IssRetido" type="tsSimNao"/>
			<xsd:element name="ValorIss" type="tsValor" minOccurs="0"/>
			<xsd:element name="ValorIssRetido" type="tsValor" minOccurs="0"/>
			<xsd:element name="OutrasRetencoes" type="tsValor" minOccurs="0"/>
			<xsd:element name="BaseCalculo" type="tsValor" minOccurs="0"/>
			<xsd:element name="Aliquota" type="tsAliquota" minOccurs="0"/>
			<xsd:element name="ValorLiquidoNfse" type="tsValor" minOccurs="0"/>
			<xsd:element name="DescontoIncondicionado" type="tsValor" minOccurs="0"/>
			<xsd:element name="DescontoCondicionado" type="tsValor" minOccurs="0"/>
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
            return f"{self.aliquota_iss:.2f}"
        return None


    @property
    def iss_retido_bool(self):
        """
        Retorna True se o ISS foi retido, False caso contrário.
        """
        return self.valor_iss_retido_centavos is not None

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
            valor_servico_centavos=int(find_text(xml, 'ValorServicos', '0').replace('.', '').replace(',', '')),
            valor_deducoes_centavos=int(find_text(xml, 'ValorDeducoes', '0').replace('.', '').replace(',', '')) if find_element(xml, 'ValorDeducoes') is not None else None,
            valor_pis_centavos=int(find_text(xml, 'ValorPis', '0').replace('.', '').replace(',', '')) if find_element(xml, 'ValorPis') is not None else None,
            valor_cofins_centavos=int(find_text(xml, 'ValorCofins', '0').replace('.', '').replace(',', '')) if find_element(xml, 'ValorCofins') is not None else None,
            valor_inss_centavos=int(find_text(xml, 'ValorInss', '0').replace('.', '').replace(',', '')) if find_element(xml, 'ValorInss') is not None else None,
            valor_ir_centavos=int(find_text(xml, 'ValorIr', '0').replace('.', '').replace(',', '')) if find_element(xml, 'ValorIr') is not None else None,
            valor_csll_centavos=int(find_text(xml, 'ValorCsll', '0').replace('.', '').replace(',', '')) if find_element(xml, 'ValorCsll') is not None else None,
            valor_iss_centavos=int(find_text(xml, 'ValorIss', '0').replace('.', '').replace(',', '')) if find_element(xml, 'ValorIss') is not None else None,
            valor_iss_retido_centavos=int(find_text(xml, 'ValorIssRetido', '0').replace('.', '').replace(',', '')) if find_element(xml, 'ValorIssRetido') is not None else None,
            outras_retencoes_centavos=int(find_text(xml, 'OutrasRetencoes', '0').replace('.', '').replace(',', '')) if find_element(xml, 'OutrasRetencoes') is not None else None,
            base_calculo_centavos=int(find_text(xml, 'BaseCalculo', '0').replace('.', '').replace(',', '')) if find_element(xml, 'BaseCalculo') is not None else None,
            aliquota_iss=float(find_text(xml, 'Aliquota', '0.00').replace(',', '.')) if find_element(xml, 'Aliquota') is not None else None,
            valor_liquido_nfse_centavos=int(find_text(xml, 'ValorLiquidoNfse', '0').replace('.', '').replace(',', '')) if find_element(xml, 'ValorLiquidoNfse') is not None else None,
            desconto_incondicionado_centavos=int(find_text(xml, 'DescontoIncondicionado', '0').replace('.', '').replace(',', '')) if find_element(xml, 'DescontoIncondicionado') is not None else None,
            desconto_condicionado_centavos=int(find_text(xml, 'DescontoCondicionado', '0').replace('.', '').replace(',', '')) if find_element(xml, 'DescontoCondicionado') is not None else None,
        )


@dataclass
class DadosServico:
    """
    <xsd:complexType name="tcDadosServico">
		<xsd:sequence>
			<xsd:element name="Valores" type="tcValores"/>
			<xsd:element name="ItemListaServico" type="tsItemListaServico"/>
			<xsd:element name="CodigoCnae" type="tsCodigoCnae" minOccurs="0"/>
			<xsd:element name="CodigoTributacaoMunicipio" type="tsCodigoTributacao" minOccurs="0"/>
			<xsd:element name="Discriminacao" type="tsDiscriminacao"/>
			<xsd:element name="CodigoMunicipio" type="tsCodigoMunicipioIbge"/>
		</xsd:sequence>
	</xsd:complexType>"""
    valores: Valores

    item_lista_servico: str
    """
    Consultar nfse/ce/fortaleza/manuais/TABELA CNAE_v_1.0-fortaleza.pdf
    """
    discriminacao: str
    """
    Texto liberal que descreve o serviço prestado.
    """

    codigo_municipio: int

    codigo_tributacao_municipio: str
    """
    Esse é o CNAE

    Consultar nfse/ce/fortaleza/manuais/TABELA CNAE_v_1.0-fortaleza.pdf
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
			<xsd:element name="Numero" type="tsNumeroRps"/>
			<xsd:element name="Serie" type="tsSerieRps"/>
			<xsd:element name="Tipo" type="tsTipoRps"/>
		</xsd:sequence>
	</xsd:complexType>
    """
    numero: str
    serie: str
    tipo: TipoRps

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
    """
    microempresa_municipal = '1'
    estimativa = '2'
    sociedade_de_profissionais = '3'
    cooperativa = '4'
    microempresario_individual = '5'
    microempresario_e_empresa_de_pequeno_porte = '6'


@dataclass
class Endereco:
    """
    <ns3:Endereco>
        <ns3:Endereco>RUA TESTE</ns3:Endereco> <!-- Tag obrigatória -->
        <ns3:Numero>123</ns3:Numero> <!-- Tag obrigatória -->
        <ns3:Complemento>APARTAMENTO 302</ns3:Complemento> <!-- Tag opcional -->
        <ns3:Bairro>TESTE</ns3:Bairro> <!-- Tag obrigatória -->
        <ns3:CodigoMunicipio>2304400</ns3:CodigoMunicipio> <!-- Tag obrigatória -->
        <ns3:Uf>CE</ns3:Uf> <!-- Tag obrigatória -->
        <ns3:Cep>60000000</ns3:Cep> <!-- Tag obrigatória -->
    </ns3:Endereco>
    """
    
    logradouro: str
    numero: str
    bairro: str
    codigo_municipio: str
    """
    abstra_notas/validacoes/cidades/municipios.json

    Busque pela cidade e utilize o campo "id"
    """
    uf: str
    cep: str
    complemento: Optional[str] = None

    def __post_init__(self):
        """
        Normaliza o campo UF.
        """
        self.uf = normalizar_uf(self.uf)
        self.cep = normalizar_cep(self.cep)
        assert self.uf, "UF deve ser fornecida."
        assert self.codigo_municipio, "Código do município deve ser fornecido."

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
            uf=find_text(xml, 'Uf', ''),
            cep=find_text(xml, 'Cep', ''),
        )

@dataclass
class Contato:
    """
    <ns3:Contato>
        <ns3:Telefone>85999999999</ns3:Telefone> <!-- Tag obrigatória -->
        <ns3:Email>contato@exemplo.com</ns3:Email> <!-- Tag obrigatória -->
    </ns3:Contato>
    """
    telefone: str
    email: str

    def __post_init__(self):
        """
        Normaliza o telefone e o email.
        """
        try:
            self.telefone = normalizar_telefone(self.telefone)
        except ValueError as e:
            warning(e)

        assert validar_email(self.email), f"Email '{self.email}' inválido. Verifique o formato do email."

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
	<xsd:complexType name="tcDadosPrestador">
		<xsd:sequence>
			<xsd:element name="IdentificacaoPrestador" type="tcIdentificacaoPrestador"/>
			<xsd:element name="RazaoSocial" type="tsRazaoSocial"/>
			<xsd:element name="NomeFantasia" type="tsNomeFantasia" minOccurs="0"/>
			<xsd:element name="Endereco" type="tcEndereco"/>
			<xsd:element name="Contato" type="tcContato" minOccurs="0"/>
		</xsd:sequence>
	</xsd:complexType>
    """

    cnpj: str
    inscricao_municipal: Optional[str]
    razao_social: str
    nome_fantasia: Optional[str]
    endereco: Endereco
    contato: Optional[Contato]

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de DadosPrestador a partir de um elemento XML.
        """
        cnpj = find_text(xml, 'Cnpj', None)
        inscricao_municipal = find_text(xml, 'InscricaoMunicipal', None)
        
        if cnpj:
            cnpj = normalizar_cnpj(cnpj)
        
        return cls(
            cnpj=cnpj,
            inscricao_municipal=inscricao_municipal,
            razao_social=find_text(xml, 'RazaoSocial', ''),
            nome_fantasia=find_text(xml, 'NomeFantasia', None),
            endereco=Endereco.from_xml(find_element(xml, 'Endereco')),
            contato=Contato.from_xml(find_element(xml, 'Contato')) if find_element(xml, 'Contato') is not None else None,
        )


@dataclass
class DadosTomador:
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

        assert self.cnpj is not None or self.cpf is not None, "CNPJ ou CPF deve ser fornecido."
    
    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de DadosTomador a partir de um elemento XML.
        """
        cnpj = find_text(xml, 'Cnpj', None)
        cpf = find_text(xml, 'Cpf', None)
        
        if cnpj:
            cnpj = normalizar_cnpj(cnpj)
        
        return cls(
            cnpj=cnpj,
            cpf=cpf,
            razao_social=find_text(xml, 'RazaoSocial', ''),
            endereco=Endereco.from_xml(find_element(xml, 'Endereco')) if find_element(xml, 'Endereco') is not None else None,
            contato=Contato.from_xml(find_element(xml, 'Contato')) if find_element(xml, 'Contato') is not None else None,
        )

@dataclass
class IdentificacaoIntermediarioServico:
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

@dataclass
class IdentificacaoOrgaoGerador:
    """
	<xsd:complexType name="tcIdentificacaoOrgaoGerador">
		<xsd:sequence>
			<xsd:element name="CodigoMunicipio" type="tsCodigoMunicipioIbge"/>
			<xsd:element name="Uf" type="tsUf"/>
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
			<xsd:element name="CodigoObra" type="tsCodigoObra"/>
			<xsd:element name="Art" type="tsArt"/>
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
			<xsd:element name="Numero" type="tsNumeroNfse"/>
			<xsd:element name="CodigoVerificacao" type="tsCodigoVerificacao"/>
			<xsd:element name="DataEmissao" type="xsd:dateTime"/>
			<xsd:element name="IdentificacaoRps" type="tcIdentificacaoRps" minOccurs="0"/>
			<xsd:element name="DataEmissaoRps" type="xsd:date" minOccurs="0"/>
			<xsd:element name="NaturezaOperacao" type="tsNaturezaOperacao"/>
			<xsd:element name="RegimeEspecialTributacao" type="tsRegimeEspecialTributacao" minOccurs="0"/>
			<xsd:element name="OptanteSimplesNacional" type="tsSimNao"/>
			<xsd:element name="IncentivadorCultural" type="tsSimNao"/>
			<xsd:element name="Competencia" type="xsd:date"/>
			<xsd:element name="NfseSubstituida" type="tsNumeroNfse" minOccurs="0"/>
			<xsd:element name="OutrasInformacoes" type="tsOutrasInformacoes" minOccurs="0"/>
			<xsd:element name="Servico" type="tcDadosServico"/>
			<xsd:element name="ValorCredito" type="tsValor" minOccurs="0"/>
			<xsd:element name="PrestadorServico" type="tcDadosPrestador"/>
			<xsd:element name="TomadorServico" type="tcDadosTomador"/>
			<xsd:element name="IntermediarioServico" type="tcIdentificacaoIntermediarioServico" minOccurs="0"/>
			<xsd:element name="OrgaoGerador" type="tcIdentificacaoOrgaoGerador"/>
			<xsd:element name="ConstrucaoCivil" type="tcDadosConstrucaoCivil" minOccurs="0"/>
		</xsd:sequence>
		<xsd:attribute name="Id" type="tsIdTag"/>
	</xsd:complexType>
    """
    numero: str
    codigo_verificacao: str
    data_emissao: datetime
    identificacao_rps: Optional[IdentificacaoRps]
    data_emissao_rps: Optional[datetime]
    natureza_operacao: Optional[str]
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
    def optante_simples_nacional_value(self):
        """
        Retorna o valor do campo optante_simples_nacional como 'S' ou 'N'.
        """
        return '1' if self.optante_simples_nacional else '2'

    @property
    def incentivador_cultural_value(self):
        """
        Retorna o valor do campo incentivador_cultural como 'S' ou 'N'.
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
            natureza_operacao=find_text(xml, 'NaturezaOperacao', ''),
            regime_especial_tributacao=RegimeEspecialTributacao(find_text(xml, 'RegimeEspecialTributacao', '')) if find_element(xml, 'RegimeEspecialTributacao') is not None else None,
            optante_simples_nacional=find_text(xml, 'OptanteSimplesNacional', 'N') == 'S',
            incentivador_cultural=find_text(xml, 'IncentivadorCultural', 'N') == 'S',
            competencia=datetime.fromisoformat(find_text(xml, 'Competencia', '')) if find_element(xml, 'Competencia') is not None else None,
            nfse_substituida=find_text(xml, 'NfseSubstituida', None),
            outras_informacoes=find_text(xml, 'OutrasInformacoes', None),
            servico=DadosServico.from_xml(find_element(xml, 'Servico')) if find_element(xml, 'Servico') is not None else None,
            valor_credito_centavos=int(find_text(xml, 'ValorCredito', '0').replace('.', '').replace(',', '')) if find_element(xml, 'ValorCredito') is not None else None,
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
			<xsd:element name="Numero" type="tsNumeroNfse"/>
			<xsd:element name="Cnpj" type="tsCnpj"/>
			<xsd:element name="InscricaoMunicipal" type="tsInscricaoMunicipal" minOccurs="0"/>
			<xsd:element name="CodigoMunicipio" type="tsCodigoMunicipioIbge"/>
		</xsd:sequence>
	</xsd:complexType>
    """
    numero: str
    cnpj: str
    inscricao_municipal: str
    codigo_municipio: str

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
			<xsd:element name="IdentificacaoNfse" type="tcIdentificacaoNfse"/>
			<xsd:element name="CodigoCancelamento" type="tsCodigoCancelamentoNfse"/>
		</xsd:sequence>
		<xsd:attribute name="Id" type="tsIdTag"/>
	</xsd:complexType>
    """
    id: str
    identificacao_nfse: IdentificacaoNfse
    codigo_cancelamento: str

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de PedidoCancelamento a partir de um elemento XML.
        """
        return cls(
            id=xml.get('Id', ''),
            identificacao_nfse=IdentificacaoNfse.from_xml(find_element(xml, 'IdentificacaoNfse')),
            codigo_cancelamento=find_text(xml, 'CodigoCancelamento', ''),
        )

@dataclass
class ConfirmacaoCancelamento:
    """
    <xsd:complexType name="tcInfConfirmacaoCancelamento">
		<xsd:sequence>
			<xsd:element name="Sucesso" type="xsd:boolean"/>
			<xsd:element name="DataHora" type="xsd:dateTime"/>
		</xsd:sequence>
	</xsd:complexType>
    """
    sucesso: bool
    data_hora: datetime

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de ConfirmacaoCancelamento a partir de um elemento XML.
        """
        return cls(
            sucesso=find_text(xml, 'Sucesso', 'false') == 'true',
            data_hora=datetime.fromisoformat(find_text(xml, 'DataHora', '')),
        )

@dataclass
class SubstituicaoNfse:
    """
    <xsd:complexType name="tcInfSubstituicaoNfse">
		<xsd:sequence>
			<xsd:element name="NfseSubstituidora" type="tsNumeroNfse"/>
		</xsd:sequence>
		<xsd:attribute name="Id" type="tsIdTag"/>
	</xsd:complexType>
    """
    id: str
    nfse_substituidora: int

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de SubstituicaoNfse a partir de um elemento XML.
        """
        return cls(
            id=xml.get('Id', ''),
            nfse_substituidora=int(find_text(xml, 'NfseSubstituidora', '0')),
        )

@dataclass
class CompNfse:
    """
    <xsd:complexType name="tcCompNfse">
		<xsd:sequence>
			<xsd:element name="Nfse" type="tcNfse"/>
			<xsd:element name="NfseCancelamento" type="tcCancelamentoNfse" minOccurs="0"/>
			<xsd:element name="NfseSubstituicao" type="tcSubstituicaoNfse" minOccurs="0"/>
		</xsd:sequence>
	</xsd:complexType>
    """
    nfse: Nfse
    cancelamento: Optional[ConfirmacaoCancelamento] = None
    substituicao: Optional[SubstituicaoNfse] = None

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de CompNfse a partir de um elemento XML.
        """
        nfse = Nfse.from_xml(find_element(xml, 'Nfse'))
        cancelamento = ConfirmacaoCancelamento.from_xml(find_element(xml, 'NfseCancelamento')) if find_element(xml, 'NfseCancelamento') is not None else None
        substituicao = SubstituicaoNfse.from_xml(find_element(xml, 'NfseSubstituicao')) if find_element(xml, 'NfseSubstituicao') is not None else None
        
        return cls(nfse=nfse, cancelamento=cancelamento, substituicao=substituicao)

@dataclass
class ConsultarNfseResposta:
    """
    <xsd:element name="ConsultarNfseResposta">
		<xsd:complexType>
			<xsd:choice>
				<xsd:element name="ListaNfse" minOccurs="1" maxOccurs="1">
					<xsd:complexType>
						<xsd:sequence>
							<xsd:element name="CompNfse" maxOccurs="unbounded" type="tipos:tcCompNfse" minOccurs="0"/>
						</xsd:sequence>
					</xsd:complexType>
				</xsd:element>
				<xsd:element ref="tipos:ListaMensagemRetorno" minOccurs="1" maxOccurs="1"/>
			</xsd:choice>
		</xsd:complexType>
        """
    comp_nfse: List[CompNfse]

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de ConsultarNfseResposta a partir de um elemento XML.
        """
        comp_nfse_elements = find_all_elements(xml, 'CompNfse')
        comp_nfse_list = [CompNfse.from_xml(comp) for comp in comp_nfse_elements]
        
        return cls(comp_nfse=comp_nfse_list)
        


@dataclass
class ConsultarNfseEnvio(Envio[ConsultarNfseResposta]):
    """
    Classe para consultar NFS-e por período de envio.
    """
    
    prestador_cnpj: str
    prestador_inscricao_municipal: str
    data_inicial: Optional[datetime] = None
    data_final: Optional[datetime] = None
    numero_nfse: Optional[int] = None

    def __post_init__(self):
        """
        Valida os dados após a inicialização da classe.
        """

        self.prestador_cnpj = normalizar_cnpj(self.prestador_cnpj)
        self.data_inicial = normalizar_data(self.data_inicial)
        self.data_final = normalizar_data(self.data_final)

    
    def nome_operacao(self):
        return "ConsultarNfseV3"
    
    def resposta(self, xml: ElementBase) -> ConsultarNfseResposta:
        return ConsultarNfseResposta.from_xml(xml)

class NaturezaOperacao(Enum):
    """
    Código de natureza da operação.
    """
    tributacao_no_municipio = '1'
    tributacao_fora_do_municipio = '2'
    isencao = '3'
    imune = '4'
    exigibilidade_suspensa_por_decisao_judicial = '5'
    exigibilidade_suspensa_por_procedimento_administrativo = '6'

@dataclass
class Rps:
    id: str
    numero: str
    serie: str
    tipo: TipoRps
    data_emissao: datetime
    natureza_operacao: NaturezaOperacao
    optante_simples_nacional: bool
    incentivador_cultural: bool
    status: StatusRps
    servico: DadosServico
    prestador_cnpj: str
    prestador_inscricao_municipal: str
    regime_especial_tributacao: Optional[RegimeEspecialTributacao] = None
    tomador_cpf: Optional[str] = None
    tomador_cnpj: Optional[str] = None
    tomador_inscricao_municipal: Optional[str] = None
    tomador_razao_social: Optional[str] = None
    tomador_endereco: Optional[Endereco] = None
    tomador_contato: Optional[Contato] = None

    @property
    def optante_simples_nacional_value(self):
        """
        Retorna o valor do campo optante_simples_nacional como 'S' ou 'N'.
        """
        return '1' if self.optante_simples_nacional else '2'

    @property
    def incentivador_cultural_value(self):
        """
        Retorna o valor do campo incentivador_cultural como 'S' ou 'N'.
        """
        return '1' if self.incentivador_cultural else '2'
    

    @property
    def data_emissao_iso8601(self):
        """
        Retorna a data de emissão no formato ISO 8601. sem o mmss
        2023-10-01T00:00:00
        """
        return self.data_emissao.strftime('%Y-%m-%dT%H:%M:%S')


    def __post_init__(self):
        """
        Valida os dados após a inicialização da classe.
        """
        self.prestador_cnpj = normalizar_cnpj(self.prestador_cnpj)
        if self.data_emissao:
            self.data_emissao = normalizar_data(self.data_emissao)
        if self.tomador_cpf:
            self.tomador_cpf = normalizar_cpf(self.tomador_cpf)
        if self.tomador_cnpj:
            self.tomador_cnpj = normalizar_cnpj(self.tomador_cnpj)
        
        assert self.tomador_cpf is not None or self.tomador_cnpj is not None, "Pelo menos um dos campos 'tomador_cpf' ou 'tomador_cnpj' deve ser preenchido."
        assert self.tomador_cnpj is None or self.tomador_razao_social is not None, "Se 'tomador_cnpj' for preenchido, 'tomador_razao_social' também deve ser preenchido."
        assert self.tomador_cnpj is None or self.tomador_endereco is not None, "Se 'tomador_cnpj' for preenchido, 'tomador_endereco' também deve ser preenchido."
        assert self.tomador_cnpj is None or self.tomador_contato is not None, "Se 'tomador_cnpj' for preenchido, 'tomador_contato' também deve ser preenchido."


    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de Rps a partir de um elemento XML.
        """
        return cls(
            numero=find_text(xml, 'Numero', ''),
            serie=find_text(xml, 'Serie', ''),
            tipo=TipoRps(find_text(xml, 'Tipo', '')),
            data_emissao=datetime.fromisoformat(find_text(xml, 'DataEmissao', '')),
            natureza_operacao=NaturezaOperacao(find_text(xml, 'NaturezaOperacao', '')),
            regime_especial_tributacao=RegimeEspecialTributacao(find_text(xml, 'RegimeEspecialTributacao', '')),
            optante_simples_nacional=find_text(xml, 'OptanteSimplesNacional', 'N') == 'S',
            incentivador_cultural=find_text(xml, 'IncentivadorCultural', 'N') == 'S',
            status=StatusRps(find_text(xml, 'Status', '')),
            servico=DadosServico.from_xml(find_element(xml, 'Servico')),
            prestador_cnpj=normalizar_cnpj(find_text(xml, 'Prestador/Cnpj', '')),
            prestador_inscricao_municipal=find_text(xml, 'Prestador/InscricaoMunicipal', ''),
            tomador_cpf=find_text(xml, 'Tomador/Cpf', ''),
            tomador_cnpj=find_text(xml, 'Tomador/Cnpj', ''),
            tomador_inscricao_municipal=find_text(xml, 'Tomador/InscricaoMunicipal', None),
            tomador_razao_social=find_text(xml, 'Tomador/RazaoSocial', None),
            tomador_endereco=Endereco.from_xml(find_element(xml, 'Tomador/Endereco')) if find_element(xml, 'Tomador/Endereco') is not None else None,
            tomador_contato=Contato.from_xml(find_element(xml, 'Tomador/Contato')) if find_element(xml, 'Tomador/Contato') is not None else None,
        )

@dataclass
class MensagemRetorno:
    """
	<xsd:complexType name="tcMensagemRetorno">
		<xsd:sequence>
			<xsd:element name="Codigo" type="tsCodigoMensagemAlerta"/>
			<xsd:element name="Mensagem" type="tsDescricaoMensagemAlerta"/>
			<xsd:element name="Correcao" type="tsDescricaoMensagemAlerta" minOccurs="0"/>
		</xsd:sequence>
	</xsd:complexType>
    """
    codigo: str
    mensagem: str
    correcao: Optional[str] = None

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
class EnviarLoteRpsResposta:
    """
    <xsd:element name="EnviarLoteRpsResposta">
		<xsd:complexType>
			<xsd:choice>
				<xsd:sequence>
					<xsd:element name="NumeroLote" type="tipos:tsNumeroLote"
						minOccurs="1" maxOccurs="1" />
					<xsd:element name="DataRecebimento" type="xsd:dateTime"
						minOccurs="1" maxOccurs="1" />
					<xsd:element name="Protocolo" type="tipos:tsNumeroProtocolo"
						minOccurs="1" maxOccurs="1" />
				</xsd:sequence>
				<xsd:element ref="tipos:ListaMensagemRetorno" minOccurs="1"
					maxOccurs="1" />
			</xsd:choice>
		</xsd:complexType>
	</xsd:element>
    """
    numero_lote: Optional[str]
    data_recebimento: Optional[datetime]
    protocolo: Optional[str]
    lista_mensagem_retorno: Optional[List[MensagemRetorno]]

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
            numero_lote=find_text(xml, 'NumeroLote', None),
            data_recebimento=datetime.fromisoformat(find_text(xml, 'DataRecebimento', '')) if find_element(xml, 'DataRecebimento') is not None else None,
            protocolo=find_text(xml, 'Protocolo', None),
            lista_mensagem_retorno=None
        )
    
@dataclass
class EnviarLoteRpsEnvio(Envio[EnviarLoteRpsResposta]):
    """
    <EnviarLoteRpsEnvio xmlns="http://www.ginfes.com.br/servico_enviar_lote_rps_envio_v03.xsd" xmlns:ns3="http://www.ginfes.com.br/tipos_v03.xsd">
	<LoteRps Id="8171">
		<ns3:NumeroLote>1234</ns3:NumeroLote> <!-- Tag obrigatória. O controle do número do lote fica a cargo do contribuinte -->
		<ns3:Cnpj>01234567891234</ns3:Cnpj> <!-- Tag obrigatória. CNPJ do prestador -->
		<ns3:InscricaoMunicipal>123456</ns3:InscricaoMunicipal> <!-- Tag obrigatória. Inscrição do prestador. Não coloque dígito verificador e nem zero à esquerda -->
		<ns3:QuantidadeRps>1</ns3:QuantidadeRps> <!-- Tag obrigatória. O lote pode ter entre 1 e 50 RPS -->
		<ns3:ListaRps> <!-- Tag obrigatória. Deve constar apenas uma vez no lote e para cada RPS, abra a tag RPS abaixo -->
			<ns3:Rps> <!-- Tag obrigatória. O número de ocorrências deve bater com a quantidade informada na tag QuantidadeRps -->
				<ns3:InfRps> <!-- Tag obrigatória -->
					<ns3:IdentificacaoRps> <!-- Tag obrigatória -->
						<ns3:Numero>2</ns3:Numero> <!-- Tag obrigatória. O controle do número do RPS fica a cargo do contribuinte -->
						<ns3:Serie>1</ns3:Serie> <!-- Tag obrigatória. O controle da série do RPS fica a cargo do contribuinte. Pode ter letras e/ou números -->
						<ns3:Tipo>1</ns3:Tipo> <!-- Tag obrigatória. 1 - RPS; 2 - Nota Fiscal Conjugada (Mista); 3 – Cupom; -->
					</ns3:IdentificacaoRps>
					<ns3:DataEmissao>2014-09-03T10:21:45</ns3:DataEmissao> <!-- Tag obrigatória. A data da emissão determina a competência  -->
					<!-- 
						Tag obrigatória. Consulte o Manual da ABRASF (link para download http://www.sefin.fortaleza.ce.gov.br/downloads/arquivos/manuais_ABRASF_1.0.zip) para saber as opções 
						de natureza de operação. 1 - Tributação no Município de Fortaleza
					-->
					<ns3:NaturezaOperacao>1</ns3:NaturezaOperacao>
					<!-- 
						Tag opcional. Se não houver (por exemplo, na tributação Normal), não coloque a tag. Consulte o Manual da ABRASF (link para download 
						http://www.sefin.fortaleza.ce.gov.br/downloads/arquivos/manuais_ABRASF_1.0.zip) para saber as opções de regime especial de tributação
					-->
					<ns3:RegimeEspecialTributacao>1</ns3:RegimeEspecialTributacao>
					<ns3:OptanteSimplesNacional>2</ns3:OptanteSimplesNacional> <!-- Tag obrigatória. Valor 1 para optante e 2 para não optante do simples nacional -->
					<ns3:IncentivadorCultural>2</ns3:IncentivadorCultural> <!-- Tag obrigatória. Valor 1 para verdadeiro e 2 para falso -->
					<ns3:Status>1</ns3:Status> <!-- Tag obrigatória. Valor 1 para normal e 2 para gerar uma nota cancelada -->
					<ns3:Servico>
						<!-- todos os valores monetários abaixo devem ficar no padrão americano sem separação de milhar. Exemplo: R$3.214,54 fica 3214.54; R$9.875.415,79 fica 9875415.79 -->
						<ns3:Valores>
							<ns3:ValorServicos>1000.00</ns3:ValorServicos> <!-- Tag obrigatória -->
							<ns3:ValorDeducoes>0.00</ns3:ValorDeducoes> <!-- Tag opcional. Somente pode ser utilizada em casos específicos -->
							<ns3:ValorPis>0.00</ns3:ValorPis> <!-- Tag opcional -->
							<ns3:ValorCofins>0.00</ns3:ValorCofins> <!-- Tag opcional -->
							<ns3:ValorInss>0.00</ns3:ValorInss> <!-- Tag opcional -->
							<ns3:ValorIr>0.00</ns3:ValorIr> <!-- Tag opcional -->
							<ns3:ValorCsll>0.00</ns3:ValorCsll> <!-- Tag opcional -->
							<!-- Tag obrigatória. Valor 1 para ISS Retido e 2 para não retido. Para saber se o tomador de Fortaleza é substituto, consulte o cartão de ISS dele no site da SEFIN -->
							<ns3:IssRetido>2</ns3:IssRetido>
							<ns3:ValorIss>50.00</ns3:ValorIss> <!-- Tag opcional. Se o ISS não for retido, preencha esta tag com o valor. Caso contrário, use a tag ValorIssRetido abaixo -->
							<ns3:ValorIssRetido>0.00</ns3:ValorIssRetido> <!-- Tag opcional. Se o ISS for retido, preencha esta tag com o valor. Caso contrário, use a tag ValorIss acima -->
							<ns3:OutrasRetencoes>0.00</ns3:OutrasRetencoes> <!-- Tag opcional -->
							<ns3:BaseCalculo>1000.0</ns3:BaseCalculo> <!-- Tag opcional. Base de Cálculo = Valor Total de Serviços - Valor de Deduções - Desconto Incondicionado -->
							<ns3:Aliquota>0.05</ns3:Aliquota> <!-- Tag opcional. A alíquota deve estar no formato decimal. 3% fica como 0.03 -->
							<!-- Tag opcional. Valor Líquido = Valor Total de Serviços - PIS - COFINS - INSS - IR - CSLL - Outras Retenções - ISS Retido - Desc. Incondicionado - Desc. Condicionado -->
							<ns3:ValorLiquidoNfse>1000.0</ns3:ValorLiquidoNfse>
							<ns3:DescontoIncondicionado>0.00</ns3:DescontoIncondicionado> <!-- Tag opcional -->
							<ns3:DescontoCondicionado>0.00</ns3:DescontoCondicionado> <!-- Tag opcional -->
						</ns3:Valores>
						<!-- Tag obrigatória. Consulte o item da lista relativo à CNAE escolhida consultando o documento com a lista de CNAEs de Fortaleza disponível na seção Layouts e 
						Documentos da página inicial do sistema -->
						<ns3:ItemListaServico>9.99</ns3:ItemListaServico>
						<!-- Tag obrigatória. Consulte a tabela de CNAEs de Fortaleza disponível na seção Layouts e Documentos da página inicial do sistema -->
						<ns3:CodigoTributacaoMunicipio>999999999</ns3:CodigoTributacaoMunicipio>
						<ns3:Discriminacao>XML DE EXEMPLO</ns3:Discriminacao> <!-- Tag obrigatória. Máximo de 2000 caracteres -->
						<ns3:CodigoMunicipio>2304400</ns3:CodigoMunicipio> <!-- Tag obrigatória. De acordo com tabela do IBGE. Código de Fortaleza: 2304400 -->
					</ns3:Servico>
					<ns3:Prestador> <!-- Tag obrigatória. -->
						<ns3:Cnpj>01234567891234</ns3:Cnpj> <!-- Tag obrigatória. CNPJ do prestador. Deve bater com o CNPJ informado no cabeçalho -->
						<ns3:InscricaoMunicipal>123456</ns3:InscricaoMunicipal> <!-- Tag opcional. Inscrição do prestador. Não deve conter o dígito verificador e bater com a inscrição do cabeçalho -->
					</ns3:Prestador>
					<ns3:Tomador> <!-- Se quiser emitir para um tomador PF ou estrangeiro sem informar qualquer dado, abra e feche a tag Tomador sem colocar qualquer conteúdo dentro -->
						<ns3:IdentificacaoTomador> <!-- Tag opcional. É possível emitir sem informar CPF, CNPJ e inscrição municipal. Neste caso, o sistema assume que a nota foi para pessoa física -->
							<ns3:CpfCnpj> <!-- Tag CpfCnpj opcional. É possível emitir sem informar CPF ou CNPJ. Neste caso o sistema assume que a nota foi emitida para uma pessoa física -->
								<ns3:Cnpj>01234567891234</ns3:Cnpj> <!-- Use a tag Cnpj para tomadores pessoa jurídica e a tag Cpf para tomadores pessoa física -->
							</ns3:CpfCnpj>
							<ns3:InscricaoMunicipal>123456</ns3:InscricaoMunicipal>	<!-- Tag opcional. Somente para tomadores de Fortaleza. Não coloque o dígito verificador -->
						</ns3:IdentificacaoTomador>
						<ns3:RazaoSocial>RAZAO SOCIAL DE EXEMPLO</ns3:RazaoSocial> <!-- Tag obrigatória para tomador pessoa jurídica -->
						<!-- Tag obrigatória para tomador pessoa jurídica. Se o tomador for pessoa física e esta tag for colocada, as tags internas <Endereco>, <Numero>, <Bairro>, <CodigoMunicipio>, <Uf> e <Cep> dever tem o conteúdo informado -->
						<ns3:Endereco>
							<ns3:Endereco>RUA TESTE</ns3:Endereco> <!-- Tag obrigatória -->
							<ns3:Numero>123</ns3:Numero> <!-- Tag obrigatória -->
							<ns3:Complemento>APARTAMENTO 302</ns3:Complemento> <!-- Tag opcional -->
							<ns3:Bairro>TESTE</ns3:Bairro> <!-- Tag obrigatória -->
							<ns3:CodigoMunicipio>2304400</ns3:CodigoMunicipio> <!-- Tag obrigatória -->
							<ns3:Uf>CE</ns3:Uf> <!-- Tag obrigatória -->
							<ns3:Cep>60000000</ns3:Cep> <!-- Tag obrigatória -->
						</ns3:Endereco>
						<ns3:Contato> <!-- Tag obrigatória para tomador pessoa jurídica -->
							<ns3:Telefone>85 31010001</ns3:Telefone> <!-- Tag obrigatória para tomador pessoa jurídica. Máximo de 11 caracteres -->
							<ns3:Email>email@exemplo.com.br</ns3:Email> <!-- Tag obrigatória para tomador pessoa jurídica. Preencha o email do tomador para que ele receba o link de visualização da nota -->
						</ns3:Contato>
					</ns3:Tomador>
				</ns3:InfRps>
			</ns3:Rps>
		</ns3:ListaRps>
	</LoteRps>
    """

    lote_id: str
    numero_lote: str
    prestador_cnpj: str
    prestador_inscricao_municipal: str
    lista_rps: List[Rps]
    quantidade_rps: int = 0

    def __post_init__(self):
        """
        Valida os dados após a inicialização da classe.
        """
        self.prestador_cnpj = normalizar_cnpj(self.prestador_cnpj)
        self.quantidade_rps = len(self.lista_rps)

    def nome_operacao(self):
        return "RecepcionarLoteRpsV3"
    
    def resposta(self, xml: ElementBase) -> CompNfse:
        if find_element(xml, 'ListaMensagemRetorno') is not None:
            mensagens = find_all_elements(xml, 'MensagemRetorno')
            lista_mensagem_retorno = [MensagemRetorno.from_xml(m) for m in mensagens]
            raise Exception(f"Erro ao enviar lote RPS: {lista_mensagem_retorno}")
        else:
            return CompNfse.from_xml(xml)

@dataclass
class CancelarNfseResposta:
    """
    <xsd:complexType>
        <xsd:sequence>
            <xsd:element name="Sucesso" type="tipos:TsSucesso" maxOccurs="1" minOccurs="1" />
            <xsd:element name="DataHora" type="tipos:TsDataHora"  maxOccurs="1" minOccurs="1" />
            <xsd:element name="MensagemRetorno" type="tipos:tcMensagemRetorno" maxOccurs="1" minOccurs="1" />
        </xsd:sequence>
    </xsd:complexType>
    """

    sucesso: bool
    data_hora: datetime
    mensagem_retorno: MensagemRetorno

    @classmethod
    def from_xml(cls, xml: ElementBase):
        """
        Método para criar uma instância de CancelarNfseResposta a partir de um elemento XML.
        """
        return cls(
            sucesso=find_text(xml, 'Sucesso', 'false') == 'true',
            data_hora=datetime.fromisoformat(find_text(xml, 'DataHora', '')),
            mensagem_retorno=MensagemRetorno.from_xml(find_element(xml, 'MensagemRetorno'))
        )

class CancelarNfseEnvio(Envio[CancelarNfseResposta]):
    prestador_cnpj: str
    prestador_inscricao_municipal: str
    numero_nfse: str

    def __post_init__(self):
        """
        Valida os dados após a inicialização da classe.
        """

        self.prestador_cnpj = normalizar_cnpj(self.prestador_cnpj)
        self.numero_nfse = str(self.numero_nfse).strip()
        assert len(self.numero_nfse) == 15, "O número da NFS-e deve ter exatamente 15 caracteres."
    
    def nome_operacao(self):
        return "CancelarNfse"

    def resposta(self, xml: ElementBase) -> CancelarNfseResposta:
        return CancelarNfseResposta.from_xml(xml)