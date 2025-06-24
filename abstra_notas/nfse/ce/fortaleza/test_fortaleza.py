import unittest
from datetime import date
from abstra_notas.nfse.ce.fortaleza import (
    EnvioRPS, 
    RPS, 
    EnvioLoteRPS, 
    ClienteMock,
    ConsultaNFe,
    CancelamentoNFe,
    ConsultaCNPJ
)
from abstra_notas.validacoes.cidades import UF


class TestFortalezaNFSe(unittest.TestCase):
    
    def setUp(self):
        self.cliente = ClienteMock()
    
    def test_criacao_rps(self):
        """Testa a criação de um RPS básico"""
        rps = RPS(
            inscricao_prestador="12345678",
            numero_rps=1,
            serie_rps="TESTE",
            data_emissao=date(2023, 1, 1),
            discriminacao="Teste de serviço",
            codigo_servico="1.01",
            aliquota_servicos=0.05,
            valor_servicos_centavos=10000,
        )
        
        self.assertEqual(rps.numero_rps, 1)
        self.assertEqual(rps.serie_rps, "TESTE")
        self.assertEqual(rps.inscricao_prestador, "12345678")
        
    def test_envio_rps(self):
        """Testa a criação de um pedido de envio de RPS"""
        pedido = EnvioRPS(
            remetente="11.222.333/0001-81",  # CNPJ válido
            inscricao_prestador="12345678",
            numero_rps=1,
            serie_rps="TESTE",
            data_emissao=date(2023, 1, 1),
            discriminacao="Teste de serviço",
            codigo_servico="1.01",
            aliquota_servicos=0.05,
            valor_servicos_centavos=10000,
            tomador_cnpj_cpf="11.444.777/0001-61",  # CNPJ válido
            tomador_razao_social="Tomador Teste",
            tomador_email="teste@teste.com",
        )
        
        self.assertEqual(pedido.remetente, "11222333000181")
        self.assertEqual(pedido.remetente_tipo, "CNPJ")
        self.assertEqual(pedido.tomador_tipo, "2")  # CNPJ
        
    def test_envio_lote_rps(self):
        """Testa a criação de um lote de RPS"""
        rps1 = RPS(
            inscricao_prestador="12345678",
            numero_rps=1,
            serie_rps="TESTE",
            data_emissao=date(2023, 1, 1),
            discriminacao="Teste de serviço 1",
            codigo_servico="1.01",
            aliquota_servicos=0.05,
            valor_servicos_centavos=10000,
        )
        
        rps2 = RPS(
            inscricao_prestador="12345678",
            numero_rps=2,
            serie_rps="TESTE",
            data_emissao=date(2023, 1, 1),
            discriminacao="Teste de serviço 2",
            codigo_servico="1.01",
            aliquota_servicos=0.05,
            valor_servicos_centavos=15000,
        )
        
        pedido = EnvioLoteRPS(
            remetente="11.222.333/0001-81",  # CNPJ válido
            numero_lote="LOTE001",
            lista_rps=[rps1, rps2]
        )
        
        self.assertEqual(pedido.quantidade_rps, 2)
        self.assertEqual(len(pedido.lista_rps), 2)
        
    def test_consulta_nfe(self):
        """Testa a criação de uma consulta de NFSe"""
        pedido = ConsultaNFe(
            remetente="11.222.333/0001-81",  # CNPJ válido
            numero_rps=1,
            serie_rps="TESTE",
            inscricao_prestador="12345678",
        )
        
        self.assertEqual(pedido.numero_rps, 1)
        self.assertEqual(pedido.serie_rps, "TESTE")
        
    def test_cancelamento_nfe(self):
        """Testa a criação de um cancelamento de NFSe"""
        pedido = CancelamentoNFe(
            remetente="11.222.333/0001-81",  # CNPJ válido
            inscricao_prestador="12345678",
            numero_nfse=123,
            codigo_cancelamento="1",
        )
        
        self.assertEqual(pedido.numero_nfse, 123)
        self.assertEqual(pedido.codigo_cancelamento, "1")
        
    def test_consulta_cnpj(self):
        """Testa a criação de uma consulta de CNPJ"""
        pedido = ConsultaCNPJ(
            remetente="11.222.333/0001-81",  # CNPJ válido
            cnpj="11.222.333/0001-81",  # CNPJ válido
        )
        
        self.assertEqual(pedido.cnpj, "11222333000181")
        
    def test_rps_com_tomador_completo(self):
        """Testa RPS com todos os dados do tomador"""
        rps = RPS(
            inscricao_prestador="12345678",
            numero_rps=1,
            serie_rps="TESTE",
            data_emissao=date(2023, 1, 1),
            discriminacao="Teste de serviço",
            codigo_servico="1.01",
            aliquota_servicos=0.05,
            valor_servicos_centavos=10000,
            tomador_cnpj_cpf="11.444.777/0001-61",  # CNPJ válido
            tomador_inscricao_municipal="87654321",
            tomador_razao_social="Empresa Tomadora LTDA",
            tomador_endereco_logradouro="Rua das Flores",
            tomador_endereco_numero="123",
            tomador_endereco_bairro="Centro",
            tomador_endereco_cidade=2304400,  # Fortaleza
            tomador_endereco_uf=UF.CEARA,
            tomador_endereco_cep="60000-000",
            tomador_telefone="(85) 99999-9999",
            tomador_email="tomador@teste.com",
        )
        
        self.assertEqual(rps.tomador_cnpj_cpf, "11444777000161")
        self.assertEqual(rps.tomador_tipo, "2")  # CNPJ
        self.assertEqual(rps.tomador_endereco_uf, UF.CEARA)
        self.assertEqual(rps.tomador_endereco_cep, "60000000")


if __name__ == '__main__':
    unittest.main()
