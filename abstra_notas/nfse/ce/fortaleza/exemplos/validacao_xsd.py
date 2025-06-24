"""
Exemplo de validação de XMLs contra XSDs de Fortaleza

Este exemplo demonstra como validar os XMLs gerados pelas classes
de NFSe de Fortaleza contra os XSDs específicos do município.
"""

import os
from datetime import date
from lxml import etree
from abstra_notas.nfse.ce.fortaleza import (
    EnvioRPS, 
    RPS, 
    EnvioLoteRPS,
    ConsultaNFe,
    CancelamentoNFe,
    ConsultaCNPJ
)
from abstra_notas.assinatura import AssinadorMock


def validar_xml_contra_xsd(xml_content, xsd_filename):
    """
    Valida um XML contra um XSD específico de Fortaleza
    
    Args:
        xml_content (str): Conteúdo XML para validar
        xsd_filename (str): Nome do arquivo XSD na pasta xsds/
        
    Returns:
        bool: True se válido, False caso contrário
    """
    try:
        # Caminho para os XSDs (sobe um nível da pasta exemplos)
        xsd_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'xsds')
        xsd_path = os.path.join(xsd_dir, xsd_filename)
        
        if not os.path.exists(xsd_path):
            print(f"XSD não encontrado: {xsd_path}")
            return False
        
        # Carrega o XSD
        with open(xsd_path, 'r', encoding='utf-8') as xsd_file:
            xsd_doc = etree.parse(xsd_file)
            xsd_schema = etree.XMLSchema(xsd_doc)
        
        # Parseia o XML
        xml_doc = etree.fromstring(xml_content.encode('utf-8'))
        
        # Valida o XML contra o XSD
        if not xsd_schema.validate(xml_doc):
            print(f"XML inválido contra XSD {xsd_filename}:")
            for error in xsd_schema.error_log:
                print(f"  Linha {error.line}: {error.message}")
            return False
        
        print(f"XML válido contra XSD {xsd_filename} ✓")
        return True
        
    except etree.XMLSyntaxError as e:
        print(f"Erro de sintaxe XML: {e}")
        return False
    except Exception as e:
        print(f"Erro na validação XSD: {e}")
        return False


def main():
    """Demonstra a validação XSD para diferentes tipos de pedido"""
    
    # Cria um assinador mock para testes
    assinador = AssinadorMock()
    
    print("=== Exemplo de Validação XSD - NFSe Fortaleza ===\n")
    
    # 1. Teste EnvioRPS
    print("1. Validando EnvioRPS...")
    pedido_rps = EnvioRPS(
        remetente="11.222.333/0001-81",
        inscricao_prestador="12345678",
        numero_rps=1,
        serie_rps="TESTE",
        data_emissao=date(2023, 1, 1),
        discriminacao="Desenvolvimento de sistema web",
        codigo_servico="1.01",
        aliquota_servicos=0.05,
        valor_servicos_centavos=10000,
        tomador_cnpj_cpf="11.444.777/0001-61",
        tomador_razao_social="Tomador Teste",
        tomador_email="teste@teste.com",
    )
    
    xml_element = pedido_rps.gerar_xml(assinador)
    xml_str = etree.tostring(xml_element, encoding='unicode', pretty_print=True)
    
    validar_xml_contra_xsd(xml_str, 'PedidoEnvioRPS_v01.xsd')
    print()
    
    # 2. Teste EnvioLoteRPS
    print("2. Validando EnvioLoteRPS...")
    rps1 = RPS(
        inscricao_prestador="12345678",
        numero_rps=1,
        serie_rps="TESTE",
        data_emissao=date(2023, 1, 1),
        discriminacao="Serviço 1",
        codigo_servico="1.01",
        aliquota_servicos=0.05,
        valor_servicos_centavos=10000,
    )
    
    rps2 = RPS(
        inscricao_prestador="12345678",
        numero_rps=2,
        serie_rps="TESTE",
        data_emissao=date(2023, 1, 1),
        discriminacao="Serviço 2",
        codigo_servico="1.01",
        aliquota_servicos=0.05,
        valor_servicos_centavos=15000,
    )
    
    pedido_lote = EnvioLoteRPS(
        remetente="11.222.333/0001-81",
        numero_lote="LOTE001",
        lista_rps=[rps1, rps2]
    )
    
    xml_element = pedido_lote.gerar_xml(assinador)
    xml_str = etree.tostring(xml_element, encoding='unicode', pretty_print=True)
    
    validar_xml_contra_xsd(xml_str, 'PedidoEnvioRPS_v01.xsd')
    print()
    
    # 3. Teste ConsultaNFe
    print("3. Validando ConsultaNFe...")
    consulta = ConsultaNFe(
        remetente="11.222.333/0001-81",
        numero_rps=1,
        serie_rps="TESTE",
        inscricao_prestador="12345678",
    )
    
    xml_element = consulta.gerar_xml(assinador)
    xml_str = etree.tostring(xml_element, encoding='unicode', pretty_print=True)
    
    validar_xml_contra_xsd(xml_str, 'ConsultaNfsePorRps_v01.xsd')
    print()
    
    # 4. Teste CancelamentoNFe
    print("4. Validando CancelamentoNFe...")
    cancelamento = CancelamentoNFe(
        remetente="11.222.333/0001-81",
        inscricao_prestador="12345678",
        numero_nfse=123,
        codigo_cancelamento="1",
    )
    
    xml_element = cancelamento.gerar_xml(assinador)
    xml_str = etree.tostring(xml_element, encoding='unicode', pretty_print=True)
    
    validar_xml_contra_xsd(xml_str, 'CancelamentoNfse_v01.xsd')
    print()
    
    # 5. Teste ConsultaCNPJ
    print("5. Validando ConsultaCNPJ...")
    consulta_cnpj = ConsultaCNPJ(
        remetente="11.222.333/0001-81",
        cnpj="11.222.333/0001-81",
    )
    
    xml_element = consulta_cnpj.gerar_xml(assinador)
    xml_str = etree.tostring(xml_element, encoding='unicode', pretty_print=True)
    
    validar_xml_contra_xsd(xml_str, 'ConsultaCnpj_v01.xsd')
    print()
    
    print("=== Validação XSD Concluída ===")


if __name__ == "__main__":
    main()
