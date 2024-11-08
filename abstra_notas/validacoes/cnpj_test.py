from unittest import TestCase
from .cnpj import normalizar_cnpj, CnpjInvalido


class TestCNPJ(TestCase):
    def test_remove_formatação(self):
        cnpj = normalizar_cnpj("02.981.391/0001-06")
        self.assertEqual(cnpj, "02981391000106")

    def test_aceita_sem_formatação(self):
        cnpj = normalizar_cnpj("02981391000106")
        self.assertEqual(cnpj, "02981391000106")

    def test_error_quantidade_de_caracteres(self):
        with self.assertRaises(CnpjInvalido):
            normalizar_cnpj("123")
