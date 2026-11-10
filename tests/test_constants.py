"""Testes unitários das constantes normativas da ABNT NBR 9077:2001."""

import unittest
from fractions import Fraction

from saidas_nbr9077.constants import (
    ALTURA_CORRIMAO_MAXIMA_M,
    ALTURA_CORRIMAO_MINIMA_M,
    ALTURA_ESPELHO_MAXIMA_M,
    ALTURA_ESPELHO_MINIMA_M,
    ALTURA_MINIMA_GUARDA_CORPO_ALTA_M,
    ALTURA_MINIMA_GUARDA_CORPO_BAIXA_M,
    BLONDEL_MAXIMO_M,
    BLONDEL_MINIMO_M,
    CAPACIDADE_UP_ESCADAS_GERAL,
    CAPACIDADE_UP_ESCADAS_REUNIAO_F,
    CAPACIDADE_UP_PORTAS_ACESSOS,
    DISTANCIA_MAX_MULTIPLA_COM_SPRINKLERS_M,
    DISTANCIA_MAX_MULTIPLA_SEM_SPRINKLERS_M,
    DISTANCIA_MAX_UNICA_COM_SPRINKLERS_M,
    DISTANCIA_MAX_UNICA_SEM_SPRINKLERS_M,
    LARGURA_LIMITE_CORRIMAO_CENTRAL_M,
    LARGURA_MINIMA_HOSPITAIS_LEITOS_M,
    LARGURA_MINIMA_SAIDA_GERAL_M,
    LARGURA_PISO_MINIMA_M,
    LARGURA_UNIDADE_PASSAGEM_M,
    VAO_MAXIMO_BARRAS_VERTICAIS_M,
)


class TestConstants(unittest.TestCase):
    """Verifica limites e coerência das constantes da NBR 9077:2001."""

    def test_unidade_passagem_e_capacidades(self) -> None:
        self.assertEqual(LARGURA_UNIDADE_PASSAGEM_M, Fraction(55, 100))
        self.assertEqual(CAPACIDADE_UP_PORTAS_ACESSOS, 100)
        self.assertEqual(CAPACIDADE_UP_ESCADAS_GERAL, 60)
        self.assertEqual(CAPACIDADE_UP_ESCADAS_REUNIAO_F, 45)

    def test_larguras_minimas(self) -> None:
        self.assertEqual(LARGURA_MINIMA_SAIDA_GERAL_M, Fraction(12, 10))
        self.assertEqual(LARGURA_MINIMA_HOSPITAIS_LEITOS_M, Fraction(22, 10))
        self.assertEqual(LARGURA_LIMITE_CORRIMAO_CENTRAL_M, Fraction(22, 10))

    def test_degraus_blondel(self) -> None:
        self.assertEqual(BLONDEL_MINIMO_M, Fraction(63, 100))
        self.assertEqual(BLONDEL_MAXIMO_M, Fraction(64, 100))
        self.assertEqual(ALTURA_ESPELHO_MINIMA_M, Fraction(16, 100))
        self.assertEqual(ALTURA_ESPELHO_MAXIMA_M, Fraction(18, 100))
        self.assertEqual(LARGURA_PISO_MINIMA_M, Fraction(27, 100))

    def test_guarda_corpos_e_corrimãos(self) -> None:
        self.assertEqual(ALTURA_MINIMA_GUARDA_CORPO_BAIXA_M, Fraction(105, 100))
        self.assertEqual(ALTURA_MINIMA_GUARDA_CORPO_ALTA_M, Fraction(130, 100))
        self.assertEqual(VAO_MAXIMO_BARRAS_VERTICAIS_M, Fraction(11, 100))
        self.assertEqual(ALTURA_CORRIMAO_MINIMA_M, Fraction(80, 100))
        self.assertEqual(ALTURA_CORRIMAO_MAXIMA_M, Fraction(92, 100))

    def test_distancias_caminhamento(self) -> None:
        self.assertEqual(DISTANCIA_MAX_UNICA_SEM_SPRINKLERS_M, Fraction(30, 1))
        self.assertEqual(DISTANCIA_MAX_MULTIPLA_SEM_SPRINKLERS_M, Fraction(45, 1))
        self.assertEqual(DISTANCIA_MAX_UNICA_COM_SPRINKLERS_M, Fraction(45, 1))
        self.assertEqual(DISTANCIA_MAX_MULTIPLA_COM_SPRINKLERS_M, Fraction(65, 1))


if __name__ == "__main__":
    unittest.main()
