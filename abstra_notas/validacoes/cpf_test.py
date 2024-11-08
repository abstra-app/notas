from unittest import TestCase
from .cpf import normalizar_cpf, CpfInvalido


class TestCPF(TestCase):
    def test_remove_formatação(self):
        cpf = normalizar_cpf("083.941.150-20")
        self.assertEqual(cpf, "08394115020")

    def test_aceita_sem_formatação(self):
        cpf = normalizar_cpf("08394115020")
        self.assertEqual(cpf, "08394115020")

    def test_error_quantidade_de_caracteres(self):
        with self.assertRaises(CpfInvalido):
            normalizar_cpf("123")
