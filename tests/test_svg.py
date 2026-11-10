"""Testes do gerador de painel técnico SVG."""

import unittest
from fractions import Fraction

from saidas_nbr9077.calculator import dimensionar_saidas_edificacao
from saidas_nbr9077.models import (
    DadosDegrau,
    DadosEdificacao,
    DadosPavimento,
    GrupoOcupacao,
    TipoEscada,
)
from saidas_nbr9077.svg_generator import gerar_painel_svg


class TestSVG(unittest.TestCase):
    """Testes de geração do diagrama vetorial SVG."""

    def test_gerar_painel_svg_estrutura(self) -> None:
        edificacao = DadosEdificacao(
            nome_edificacao="Complexo Comercial Beta",
            altura_total_m=Fraction(36, 1),
            tipo_escada=TipoEscada.PRESSURIZADA,
            possui_sprinklers=True,
            dados_degrau=DadosDegrau(altura_espelho_m=Fraction(175, 1000), largura_piso_m=Fraction(280, 1000)),
            pavimentos=(
                DadosPavimento(
                    nome_pavimento="Térreo",
                    grupo_ocupacao=GrupoOcupacao.C_COMERCIAL,
                    area_liquida_m2=Fraction(800, 1),
                    distancia_percorrer_m=Fraction(30, 1),
                    quantidade_saidas_instaladas=3,
                ),
                DadosPavimento(
                    nome_pavimento="1º Andar",
                    grupo_ocupacao=GrupoOcupacao.D_SERVICOS_PROFISSIONAIS,
                    area_liquida_m2=Fraction(600, 1),
                    distancia_percorrer_m=Fraction(22, 1),
                    quantidade_saidas_instaladas=2,
                ),
            ),
        )
        res = dimensionar_saidas_edificacao(edificacao)
        svg = gerar_painel_svg(res)

        self.assertIsInstance(svg, str)
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.strip().endswith("</svg>"))
        self.assertIn('viewBox="0 0 1440 900"', svg)
        self.assertIn("Complexo Comercial Beta", svg)
        self.assertIn("ABNT NBR 9077:2001", svg)
        self.assertIn("LOFRANO TECNOLOGIA", svg)
        self.assertIn("ESQUEMA DE ROTAS DE FUGA E CAIXA DE ESCADA", svg)
        self.assertIn("ERGONOMIA DE DEGRAUS (BLONDEL)", svg)

    def test_gerar_painel_svg_degrau_inconforme(self) -> None:
        edificacao = DadosEdificacao(
            nome_edificacao="Edifício Alerta",
            altura_total_m=Fraction(9, 1),
            tipo_escada=TipoEscada.NAO_ENCLAUSURADA,
            possui_sprinklers=False,
            # Blondel violado: 2*0.22 + 0.22 = 0.66 > 0.64
            dados_degrau=DadosDegrau(altura_espelho_m=Fraction(22, 100), largura_piso_m=Fraction(22, 100)),
            pavimentos=(
                DadosPavimento(
                    nome_pavimento="Único",
                    grupo_ocupacao=GrupoOcupacao.A_RESIDENCIAL,
                    area_liquida_m2=Fraction(200, 1),
                    distancia_percorrer_m=Fraction(15, 1),
                    quantidade_saidas_instaladas=1,
                ),
            ),
        )
        res = dimensionar_saidas_edificacao(edificacao)
        svg = gerar_painel_svg(res)
        self.assertIn("Edifício Alerta", svg)
        self.assertIn("NÃO CONFORME", svg)


if __name__ == "__main__":
    unittest.main()
