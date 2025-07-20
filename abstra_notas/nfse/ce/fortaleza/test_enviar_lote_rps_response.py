#!/usr/bin/env python3
"""
Testes unitários para o parsing da resposta do EnviarLoteRpsEnvio
Usa respostas mock para testar sem fazer requests reais.
"""

import unittest
from datetime import datetime
from lxml.etree import fromstring
from abstra_notas.nfse.ce.fortaleza import EnviarLoteRpsEnvio


class TestEnviarLoteRpsResponseParsing(unittest.TestCase):
    """Testes para o parsing das respostas do EnviarLoteRpsEnvio"""

    def setUp(self):
        """Configuração comum para todos os testes"""
        self.envio = EnviarLoteRpsEnvio(
            lote_id="LOTE001",
            numero_lote="123", 
            prestador_cnpj="11.222.333/0001-81",
            prestador_inscricao_municipal="123456",
            lista_rps=[]
        )

    def test_response_parsing_success(self):
        """Testa o parsing de uma resposta de sucesso"""
        # XML de resposta de sucesso mock
        response_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <EnviarLoteRpsResposta xmlns="http://www.ginfes.com.br/servico_enviar_lote_rps_resposta_v03.xsd" xmlns:ns2="http://www.ginfes.com.br/tipos_v03.xsd">
            <NumeroLote>123</NumeroLote>
            <DataRecebimento>2024-01-15T14:30:25.123-03:00</DataRecebimento>
            <Protocolo>987654321</Protocolo>
        </EnviarLoteRpsResposta>"""
        
        # Parse do XML
        xml_resposta = fromstring(response_xml.encode("utf-8"))
        
        # Executar parsing
        resultado = self.envio.resposta(xml_resposta)
        
        # Validações
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.numero_lote, "123")
        self.assertEqual(resultado.protocolo, "987654321")
        self.assertIsNone(resultado.lista_mensagem_retorno)
        self.assertIsInstance(resultado.data_recebimento, datetime)
        
        # Verificar que a data foi parseada corretamente
        expected_date = datetime.fromisoformat("2024-01-15T14:30:25.123-03:00")
        self.assertEqual(resultado.data_recebimento, expected_date)

    def test_response_parsing_error(self):
        """Testa o parsing de uma resposta com erro"""
        # XML de resposta com erro mock
        response_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <EnviarLoteRpsResposta xmlns="http://www.ginfes.com.br/servico_enviar_lote_rps_resposta_v03.xsd" xmlns:ns2="http://www.ginfes.com.br/tipos_v03.xsd">
            <ns2:ListaMensagemRetorno>
                <ns2:MensagemRetorno>
                    <ns2:Codigo>E999</ns2:Codigo>
                    <ns2:Mensagem>Erro de teste para validação.</ns2:Mensagem>
                    <ns2:Correcao>Corrigir dados de teste.</ns2:Correcao>
                </ns2:MensagemRetorno>
            </ns2:ListaMensagemRetorno>
        </EnviarLoteRpsResposta>"""
        
        # Parse do XML
        xml_resposta = fromstring(response_xml.encode("utf-8"))
        
        # Executar parsing
        resultado = self.envio.resposta(xml_resposta)
        
        # Validações
        self.assertIsNotNone(resultado)
        self.assertIsNone(resultado.numero_lote)
        self.assertIsNone(resultado.data_recebimento)
        self.assertIsNone(resultado.protocolo)
        self.assertIsNotNone(resultado.lista_mensagem_retorno)
        self.assertEqual(len(resultado.lista_mensagem_retorno), 1)
        
        # Verificar mensagem de erro
        erro = resultado.lista_mensagem_retorno[0]
        self.assertEqual(erro.codigo, "E999")
        self.assertEqual(erro.mensagem, "Erro de teste para validação.")
        self.assertEqual(erro.correcao, "Corrigir dados de teste.")

    def test_response_parsing_multiple_errors(self):
        """Testa o parsing de uma resposta com múltiplos erros"""
        # XML de resposta com múltiplos erros mock
        response_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <EnviarLoteRpsResposta xmlns="http://www.ginfes.com.br/servico_enviar_lote_rps_resposta_v03.xsd" xmlns:ns2="http://www.ginfes.com.br/tipos_v03.xsd">
            <ns2:ListaMensagemRetorno>
                <ns2:MensagemRetorno>
                    <ns2:Codigo>E001</ns2:Codigo>
                    <ns2:Mensagem>Primeiro erro de teste.</ns2:Mensagem>
                    <ns2:Correcao>Corrigir primeiro problema.</ns2:Correcao>
                </ns2:MensagemRetorno>
                <ns2:MensagemRetorno>
                    <ns2:Codigo>E002</ns2:Codigo>
                    <ns2:Mensagem>Segundo erro de teste.</ns2:Mensagem>
                    <ns2:Correcao>Corrigir segundo problema.</ns2:Correcao>
                </ns2:MensagemRetorno>
            </ns2:ListaMensagemRetorno>
        </EnviarLoteRpsResposta>"""
        
        # Parse do XML
        xml_resposta = fromstring(response_xml.encode("utf-8"))
        
        # Executar parsing
        resultado = self.envio.resposta(xml_resposta)
        
        # Validações
        self.assertIsNotNone(resultado)
        self.assertIsNone(resultado.numero_lote)
        self.assertIsNone(resultado.data_recebimento)
        self.assertIsNone(resultado.protocolo)
        self.assertIsNotNone(resultado.lista_mensagem_retorno)
        self.assertEqual(len(resultado.lista_mensagem_retorno), 2)
        
        # Verificar primeira mensagem de erro
        erro1 = resultado.lista_mensagem_retorno[0]
        self.assertEqual(erro1.codigo, "E001")
        self.assertEqual(erro1.mensagem, "Primeiro erro de teste.")
        
        # Verificar segunda mensagem de erro
        erro2 = resultado.lista_mensagem_retorno[1]
        self.assertEqual(erro2.codigo, "E002")
        self.assertEqual(erro2.mensagem, "Segundo erro de teste.")

    def test_response_type_validation(self):
        """Testa se o tipo de resposta retornado é correto"""
        response_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <EnviarLoteRpsResposta xmlns="http://www.ginfes.com.br/servico_enviar_lote_rps_resposta_v03.xsd" xmlns:ns2="http://www.ginfes.com.br/tipos_v03.xsd">
            <NumeroLote>456</NumeroLote>
            <DataRecebimento>2024-02-20T09:15:30.456-03:00</DataRecebimento>
            <Protocolo>123456789</Protocolo>
        </EnviarLoteRpsResposta>"""
        
        # Parse do XML
        xml_resposta = fromstring(response_xml.encode("utf-8"))
        
        # Executar parsing
        resultado = self.envio.resposta(xml_resposta)
        
        # Validar tipo da resposta
        from abstra_notas.nfse.ce.fortaleza import EnviarLoteRpsResposta
        self.assertIsInstance(resultado, EnviarLoteRpsResposta)

    def test_empty_response_handling(self):
        """Testa o comportamento com uma resposta mínima válida"""
        response_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <EnviarLoteRpsResposta xmlns="http://www.ginfes.com.br/servico_enviar_lote_rps_resposta_v03.xsd" xmlns:ns2="http://www.ginfes.com.br/tipos_v03.xsd">
        </EnviarLoteRpsResposta>"""
        
        # Parse do XML
        xml_resposta = fromstring(response_xml.encode("utf-8"))
        
        # Executar parsing
        resultado = self.envio.resposta(xml_resposta)
        
        # Validações - campos devem ser None quando não presentes
        self.assertIsNotNone(resultado)
        self.assertIsNone(resultado.numero_lote)
        self.assertIsNone(resultado.data_recebimento)
        self.assertIsNone(resultado.protocolo)
        self.assertIsNone(resultado.lista_mensagem_retorno)


if __name__ == '__main__':
    unittest.main()
