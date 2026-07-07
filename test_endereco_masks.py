import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "SistemaDesktop"))

from services.endereco_service import (
    formatar_cep,
    formatar_uf,
    formatar_cidade,
    buscar_cep,
)


class TestEnderecoMasks(unittest.TestCase):
    def test_formatar_cep(self):
        self.assertEqual(formatar_cep("1"), ("1", 1))
        self.assertEqual(formatar_cep("12345"), ("12345", 5))
        self.assertEqual(formatar_cep("1234567"), ("12345-67", 8))
        self.assertEqual(formatar_cep("123456789"), ("12345-678", 9))

    def test_formatar_uf(self):
        self.assertEqual(formatar_uf("sp"), ("SP", 2))
        self.assertEqual(formatar_uf("s1p"), ("SP", 2))
        self.assertEqual(formatar_uf("sao paulo"), ("SA", 2))

    def test_formatar_cidade(self):
        self.assertEqual(formatar_cidade("sao luis"), ("São Luis", 8))
        self.assertEqual(formatar_cidade("rio de janeiro"), ("Rio de Janeiro", 14))

    def test_buscar_cep(self):
        resultado = buscar_cep("00000000")
        self.assertIsNone(resultado)


if __name__ == "__main__":
    unittest.main()
