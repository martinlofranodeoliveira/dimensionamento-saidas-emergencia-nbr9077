"""Testes de casos avançados e cenários normativos complexos da NBR 9077:2001."""

import unittest
from fractions import Fraction

from saidas_nbr9077.calculator import (
    dimensionar_pavimento,
    dimensionar_saidas_edificacao,
    verificar_degraus_blondel,
)
from saidas_nbr9077.constants import (
    ALTURA_MINIMA_GUARDA_CORPO_ALTA_M,
    ALTURA_MINIMA_GUARDA_CORPO_BAIXA_M,
    LARGURA_MINIMA_HOSPITAIS_LEITOS_M,
    LARGURA_MINIMA_REUNIAO_GRANDE_M,
    LARGURA_MINIMA_SAIDA_GERAL_M,
)
from saidas_nbr9077.models import (
    DadosDegrau,
    DadosEdificacao,
    DadosPavimento,
    GrupoOcupacao,
    TipoEscada,
)


class TestCasosAvancados(unittest.TestCase):
    """Bateria de testes aprofundados para cenários de alta complexidade técnica."""

    def test_reuniao_publico_populacao_massiva_exige_largura_220m(self) -> None:
        """Locais de reunião F com > 300 pessoas devem exigir largura mínima de 2,20m."""
        pav = DadosPavimento(
            nome_pavimento="Auditório Principal",
            grupo_ocupacao=GrupoOcupacao.F_REUNIAO_PUBLICO,
            area_liquida_m2=Fraction(400, 1),  # Fator 1 pessoa / m² -> 400 pessoas
            distancia_percorrer_m=Fraction(20, 1),
            quantidade_saidas_instaladas=3,
        )
        alertas: list[str] = []
        res = dimensionar_pavimento(pav, possui_sprinklers=False, alertas=alertas)

        self.assertEqual(res.populacao_calculada, 400)
        # Portas: 400 / 100 = 4 UP -> 4 * 0.55 = 2.20 m
        self.assertEqual(res.unidades_passagem_portas, 4)
        self.assertEqual(res.largura_minima_portas_m, Fraction(22, 10))

        # Escadas para grupo F: C = 45 -> teto(400/45) = 9 UP -> 9 * 0.55 = 4.95 m
        self.assertEqual(res.unidades_passagem_escadas, 9)
        self.assertEqual(res.largura_minima_escadas_m, Fraction(495, 100))
        self.assertGreaterEqual(res.largura_minima_escadas_m, LARGURA_MINIMA_REUNIAO_GRANDE_M)

    def test_hospital_sempre_exige_largura_220m_mesmo_populacao_baixa(self) -> None:
        """Hospitais (Grupo H) com internação exigem 2,20m de portas/corredores para transporte de leitos."""
        pav = DadosPavimento(
            nome_pavimento="Ala de Internação",
            grupo_ocupacao=GrupoOcupacao.H_SERVICOS_SAUDE,
            area_liquida_m2=Fraction(50, 1),  # Poucas pessoas
            distancia_percorrer_m=Fraction(15, 1),
            quantidade_saidas_instaladas=2,
        )
        alertas: list[str] = []
        res = dimensionar_pavimento(pav, possui_sprinklers=False, alertas=alertas)

        self.assertEqual(res.largura_minima_portas_m, LARGURA_MINIMA_HOSPITAIS_LEITOS_M)
        self.assertEqual(res.largura_minima_escadas_m, LARGURA_MINIMA_HOSPITAIS_LEITOS_M)

    def test_edificacao_larga_exige_corrimao_central(self) -> None:
        """Escadas com largura > 2,20m devem acusar exigência de corrimão central."""
        edificacao = DadosEdificacao(
            nome_edificacao="Arena Multiuso",
            altura_total_m=Fraction(15, 1),
            tipo_escada=TipoEscada.ENCLAUSURADA_FUMACA,
            possui_sprinklers=True,
            dados_degrau=DadosDegrau(altura_espelho_m=Fraction(17, 100), largura_piso_m=Fraction(30, 100)),
            pavimentos=(
                DadosPavimento(
                    nome_pavimento="Plateia",
                    grupo_ocupacao=GrupoOcupacao.F_REUNIAO_PUBLICO,
                    area_liquida_m2=Fraction(300, 1),  # 300 pessoas -> 7 UP escada = 3.85m
                    distancia_percorrer_m=Fraction(25, 1),
                    quantidade_saidas_instaladas=4,
                ),
            ),
        )
        res = dimensionar_saidas_edificacao(edificacao)
        self.assertTrue(res.guarda_corpo.exige_corrimao_central)
        self.assertTrue(any("corrimão intermediário central" in r for r in res.recomendacoes))

    def test_distancia_caminhamento_com_e_sem_sprinklers(self) -> None:
        """Compara limites de distância única e múltipla com ou sem sprinklers."""
        # Sem sprinklers, saída única: máx 30m
        p_unica_sem = DadosPavimento(
            nome_pavimento="P1",
            grupo_ocupacao=GrupoOcupacao.D_SERVICOS_PROFISSIONAIS,
            area_liquida_m2=Fraction(100, 1),
            distancia_percorrer_m=Fraction(28, 1),
            quantidade_saidas_instaladas=1,
        )
        res1 = dimensionar_pavimento(p_unica_sem, possui_sprinklers=False)
        self.assertTrue(res1.conforme_distancia)
        self.assertEqual(res1.distancia_maxima_permitida_m, Fraction(30, 1))

        # Sem sprinklers, ultrapassa 30m em saída única
        p_unica_sem_longa = DadosPavimento(
            nome_pavimento="P1_Longa",
            grupo_ocupacao=GrupoOcupacao.D_SERVICOS_PROFISSIONAIS,
            area_liquida_m2=Fraction(100, 1),
            distancia_percorrer_m=Fraction(35, 1),
            quantidade_saidas_instaladas=1,
        )
        res2 = dimensionar_pavimento(p_unica_sem_longa, possui_sprinklers=False)
        self.assertFalse(res2.conforme_distancia)

        # Com sprinklers e saídas múltiplas: limite expande para 65m
        p_mult_com = DadosPavimento(
            nome_pavimento="P2",
            grupo_ocupacao=GrupoOcupacao.D_SERVICOS_PROFISSIONAIS,
            area_liquida_m2=Fraction(1000, 1),
            distancia_percorrer_m=Fraction(60, 1),
            quantidade_saidas_instaladas=2,
        )
        res3 = dimensionar_pavimento(p_mult_com, possui_sprinklers=True)
        self.assertTrue(res3.conforme_distancia)
        self.assertEqual(res3.distancia_maxima_permitida_m, Fraction(65, 1))

    def test_populacao_fixada_prevalece_sobre_calculada(self) -> None:
        """Quando populacao_fixada é fornecida, ela deve ser usada para o dimensionamento."""
        p_fixada = DadosPavimento(
            nome_pavimento="Sala Técnica",
            grupo_ocupacao=GrupoOcupacao.D_SERVICOS_PROFISSIONAIS,
            area_liquida_m2=Fraction(1000, 1),  # Por área daria 143 pessoas
            distancia_percorrer_m=Fraction(10, 1),
            quantidade_saidas_instaladas=1,
            populacao_fixada=10,  # Apenas 10 operadores autorizados
        )
        res = dimensionar_pavimento(p_fixada, possui_sprinklers=False)
        self.assertEqual(res.populacao_calculada, 10)
        self.assertEqual(res.unidades_passagem_portas, 2)  # Mínimo regulamentar de 2 UP

    def test_blondel_limites_exatos(self) -> None:
        """Verifica os limites exatos da fórmula de Blondel (63 cm e 64 cm)."""
        # Limite inferior exato: h = 0.175, b = 0.280 -> 2*0.175 + 0.280 = 0.630 m
        deg_min = DadosDegrau(altura_espelho_m=Fraction(175, 1000), largura_piso_m=Fraction(280, 1000))
        res_min = verificar_degraus_blondel(deg_min)
        self.assertTrue(res_min.conforme_blondel)
        self.assertTrue(res_min.conforme_geral)
        self.assertEqual(res_min.valor_blondel_m, Fraction(63, 100))

        # Limite superior exato: h = 0.170, b = 0.300 -> 2*0.170 + 0.300 = 0.640 m
        deg_max = DadosDegrau(altura_espelho_m=Fraction(170, 1000), largura_piso_m=Fraction(300, 1000))
        res_max = verificar_degraus_blondel(deg_max)
        self.assertTrue(res_max.conforme_blondel)
        self.assertTrue(res_max.conforme_geral)
        self.assertEqual(res_max.valor_blondel_m, Fraction(64, 100))

        # Violação superior: 2*0.18 + 0.30 = 0.66 > 0.64
        deg_acima = DadosDegrau(altura_espelho_m=Fraction(18, 100), largura_piso_m=Fraction(30, 100))
        res_acima = verificar_degraus_blondel(deg_acima)
        self.assertFalse(res_acima.conforme_blondel)
        self.assertFalse(res_acima.conforme_geral)

    def test_espelho_invalido_baixo_e_alto(self) -> None:
        """Espelho deve estar estritamente entre 16 cm e 18 cm."""
        # Espelho < 16 cm (ex: 15 cm)
        deg_baixo = DadosDegrau(altura_espelho_m=Fraction(15, 100), largura_piso_m=Fraction(33, 100))
        res_baixo = verificar_degraus_blondel(deg_baixo)
        self.assertFalse(res_baixo.conforme_espelho)
        self.assertFalse(res_baixo.conforme_geral)

        # Espelho > 18 cm (ex: 19 cm)
        deg_alto = DadosDegrau(altura_espelho_m=Fraction(19, 100), largura_piso_m=Fraction(27, 100))
        res_alto = verificar_degraus_blondel(deg_alto)
        self.assertFalse(res_alto.conforme_espelho)
        self.assertFalse(res_alto.conforme_geral)

    def test_piso_invalido_menor_que_27cm(self) -> None:
        """Piso deve ser maior ou igual a 27 cm."""
        deg_curto = DadosDegrau(altura_espelho_m=Fraction(18, 100), largura_piso_m=Fraction(26, 100))
        res_curto = verificar_degraus_blondel(deg_curto)
        self.assertFalse(res_curto.conforme_piso)
        self.assertFalse(res_curto.conforme_geral)


if __name__ == "__main__":
    unittest.main()
