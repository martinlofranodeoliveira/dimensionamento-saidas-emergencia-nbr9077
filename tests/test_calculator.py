"""Testes unitários do motor de cálculo da NBR 9077."""

import unittest
from fractions import Fraction

from saidas_nbr9077.calculator import (
    _teto_fracao,
    dimensionar_pavimento,
    dimensionar_saidas_edificacao,
    obter_fator_area_por_pessoa,
    verificar_degraus_blondel,
)
from saidas_nbr9077.constants import (
    ALTURA_MINIMA_GUARDA_CORPO_ALTA_M,
    ALTURA_MINIMA_GUARDA_CORPO_BAIXA_M,
    LARGURA_MINIMA_HOSPITAIS_LEITOS_M,
    LARGURA_MINIMA_SAIDA_GERAL_M,
)
from saidas_nbr9077.models import (
    DadosDegrau,
    DadosEdificacao,
    DadosPavimento,
    GrupoOcupacao,
    TipoEscada,
)


class TestCalculator(unittest.TestCase):
    """Testa cálculos de população, unidades de passagem, Blondel e caminhamento."""

    def test_teto_fracao(self) -> None:
        self.assertEqual(_teto_fracao(Fraction(10, 1)), 10)
        self.assertEqual(_teto_fracao(Fraction(0, 1)), 0)
        self.assertEqual(_teto_fracao(Fraction(7, 2)), 4)
        self.assertEqual(_teto_fracao(Fraction(1, 5)), 1)
        self.assertEqual(_teto_fracao(Fraction(25, 4)), 7)

    def test_fatores_area_por_pessoa(self) -> None:
        self.assertEqual(obter_fator_area_por_pessoa(GrupoOcupacao.A_RESIDENCIAL), Fraction(15, 1))
        self.assertEqual(obter_fator_area_por_pessoa(GrupoOcupacao.D_SERVICOS_PROFISSIONAIS), Fraction(7, 1))
        self.assertEqual(obter_fator_area_por_pessoa(GrupoOcupacao.E_EDUCACIONAL), Fraction(2, 1))
        self.assertEqual(obter_fator_area_por_pessoa(GrupoOcupacao.F_REUNIAO_PUBLICO), Fraction(1, 1))

    def test_verificar_degraus_blondel_conforme(self) -> None:
        deg = DadosDegrau(
            altura_espelho_m=Fraction(175, 1000),  # 0.175 m
            largura_piso_m=Fraction(285, 1000),   # 0.285 m
        )
        res = verificar_degraus_blondel(deg)
        # 2 * 0.175 + 0.285 = 0.635 m (está entre 0.63 e 0.64 m)
        self.assertEqual(res.valor_blondel_m, Fraction(635, 1000))
        self.assertTrue(res.conforme_blondel)
        self.assertTrue(res.conforme_espelho)
        self.assertTrue(res.conforme_piso)
        self.assertTrue(res.conforme_geral)

    def test_verificar_degraus_blondel_inconforme(self) -> None:
        deg = DadosDegrau(
            altura_espelho_m=Fraction(20, 100),   # 0.20 m (> 0.18 m)
            largura_piso_m=Fraction(25, 100),    # 0.25 m (< 0.27 m)
        )
        res = verificar_degraus_blondel(deg)
        self.assertFalse(res.conforme_espelho)
        self.assertFalse(res.conforme_piso)
        self.assertFalse(res.conforme_geral)

    def test_dimensionar_pavimento_escritorios(self) -> None:
        alertas: list[str] = []
        pav = DadosPavimento(
            nome_pavimento="Escritórios",
            grupo_ocupacao=GrupoOcupacao.D_SERVICOS_PROFISSIONAIS,
            area_liquida_m2=Fraction(420, 1),
            distancia_percorrer_m=Fraction(25, 1),
            quantidade_saidas_instaladas=2,
        )
        res = dimensionar_pavimento(pav, possui_sprinklers=True, alertas=alertas)
        # 420 / 7 = 60 pessoas
        self.assertEqual(res.populacao_calculada, 60)
        # 60 / 100 = 1 UP -> mínimo normativo é 2 UP
        self.assertEqual(res.unidades_passagem_portas, 2)
        # 60 / 60 = 1 UP -> mínimo normativo é 2 UP
        self.assertEqual(res.unidades_passagem_escadas, 2)
        self.assertEqual(res.largura_minima_portas_m, LARGURA_MINIMA_SAIDA_GERAL_M)
        self.assertEqual(res.largura_minima_escadas_m, LARGURA_MINIMA_SAIDA_GERAL_M)
        self.assertTrue(res.conforme_distancia)
        self.assertTrue(res.conforme_saidas)

    def test_dimensionar_pavimento_hospital_largura_220m(self) -> None:
        alertas: list[str] = []
        pav = DadosPavimento(
            nome_pavimento="Enfermaria",
            grupo_ocupacao=GrupoOcupacao.H_SERVICOS_SAUDE,
            area_liquida_m2=Fraction(300, 1),
            distancia_percorrer_m=Fraction(20, 1),
            quantidade_saidas_instaladas=2,
        )
        res = dimensionar_pavimento(pav, possui_sprinklers=False, alertas=alertas)
        # Hospitais com leitos exigem largura mínima de 2,20 m
        self.assertEqual(res.largura_minima_portas_m, LARGURA_MINIMA_HOSPITAIS_LEITOS_M)
        self.assertEqual(res.largura_minima_escadas_m, LARGURA_MINIMA_HOSPITAIS_LEITOS_M)

    def test_guarda_corpo_alta_edificacao(self) -> None:
        deg = DadosDegrau(Fraction(17, 100), Fraction(29, 100))
        p = DadosPavimento("Térreo", GrupoOcupacao.D_SERVICOS_PROFISSIONAIS, Fraction(300, 1), Fraction(15, 1), 2)
        ed_baixa = DadosEdificacao("Prédio Baixo", Fraction(10, 1), TipoEscada.ENCLAUSURADA_PROTEGIDA, False, deg, (p,))
        ed_alta = DadosEdificacao("Prédio Alto", Fraction(25, 1), TipoEscada.ENCLAUSURADA_PROTEGIDA, False, deg, (p,))

        res_baixa = dimensionar_saidas_edificacao(ed_baixa)
        res_alta = dimensionar_saidas_edificacao(ed_alta)

        self.assertEqual(res_baixa.guarda_corpo.altura_minima_guarda_corpo_m, ALTURA_MINIMA_GUARDA_CORPO_BAIXA_M)
        self.assertEqual(res_alta.guarda_corpo.altura_minima_guarda_corpo_m, ALTURA_MINIMA_GUARDA_CORPO_ALTA_M)


if __name__ == "__main__":
    unittest.main()
