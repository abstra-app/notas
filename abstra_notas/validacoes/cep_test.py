from unittest import TestCase
from .cep import normalizar_cep


class CepTest(TestCase):
    def test_valido(self):
        normalizado = normalizar_cep("01310-100")
        self.assertEqual(normalizado, "01310100")

    def test_valido_sem_traco(self):
        normalizado = normalizar_cep("01310100")
        self.assertEqual(normalizado, "01310100")

    def test_valido_com_ponto(self):
        normalizado = normalizar_cep("013.10100")
        self.assertEqual(normalizado, "01310100")

    def test_menor_que_8_digitos(self):
        normalizado = normalizar_cep("1310100")
        self.assertEqual(normalizado, "01310100")

    def test_maior_que_8_digitos(self):
        with self.assertRaises(AssertionError):
            normalizar_cep("131010123123")
