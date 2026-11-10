"""Testes unitários dos modelos e dataclasses da NBR 9077."""

import unittest
from fractions import Fraction

from saidas_nbr9077.models import (
    DadosDegrau,
    DadosEdificacao,
    DadosPavimento,
    GrupoOcupacao,
    TipoEscada,
)


class TestModels(unittest.TestCase):
    """Verifica instanciação, imutabilidade e validações dos modelos."""

    def test_enums(self) -> None:
        self.assertEqual(GrupoOcupacao.A_RESIDENCIAL.value, "A")
        self.assertEqual(GrupoOcupacao.F_REUNIAO_PUBLICO.value, "F")
        self.assertEqual(TipoEscada.ENCLAUSURADA_PROTEGIDA.value, "enclausurada_protegida")
        self.assertEqual(TipoEscada.ENCLAUSURADA_FUMACA.value, "enclausurada_a_prova_de_fumaca")

    def test_dados_degrau_valido(self) -> None:
        d = DadosDegrau(
            altura_espelho_m=Fraction(17, 100),
            largura_piso_m=Fraction(29, 100),
        )
        self.assertEqual(d.altura_espelho_m, Fraction(17, 100))
        self.assertEqual(d.largura_piso_m, Fraction(29, 100))

    def test_dados_degrau_invalido(self) -> None:
        with self.assertRaises(ValueError):
            DadosDegrau(altura_espelho_m=Fraction(0, 1), largura_piso_m=Fraction(28, 100))
        with self.assertRaises(ValueError):
            DadosDegrau(altura_espelho_m=Fraction(17, 100), largura_piso_m=Fraction(-1, 100))

    def test_dados_pavimento_valido(self) -> None:
        p = DadosPavimento(
            nome_pavimento="Térreo",
            grupo_ocupacao=GrupoOcupacao.D_SERVICOS_PROFISSIONAIS,
            area_liquida_m2=Fraction(400, 1),
            distancia_percorrer_m=Fraction(20, 1),
            quantidade_saidas_instaladas=2,
        )
        self.assertEqual(p.nome_pavimento, "Térreo")
        self.assertEqual(p.area_liquida_m2, Fraction(400, 1))

    def test_dados_pavimento_invalido(self) -> None:
        with self.assertRaises(ValueError):
            DadosPavimento(
                nome_pavimento="",
                grupo_ocupacao=GrupoOcupacao.D_SERVICOS_PROFISSIONAIS,
                area_liquida_m2=Fraction(400, 1),
                distancia_percorrer_m=Fraction(20, 1),
                quantidade_saidas_instaladas=2,
            )
        with self.assertRaises(ValueError):
            DadosPavimento(
                nome_pavimento="Térreo",
                grupo_ocupacao=GrupoOcupacao.D_SERVICOS_PROFISSIONAIS,
                area_liquida_m2=Fraction(-10, 1),
                distancia_percorrer_m=Fraction(20, 1),
                quantidade_saidas_instaladas=2,
            )
        with self.assertRaises(ValueError):
            DadosPavimento(
                nome_pavimento="Térreo",
                grupo_ocupacao=GrupoOcupacao.D_SERVICOS_PROFISSIONAIS,
                area_liquida_m2=Fraction(400, 1),
                distancia_percorrer_m=Fraction(20, 1),
                quantidade_saidas_instaladas=0,
            )

    def test_dados_edificacao_valido(self) -> None:
        deg = DadosDegrau(Fraction(17, 100), Fraction(28, 100))
        p = DadosPavimento("Térreo", GrupoOcupacao.D_SERVICOS_PROFISSIONAIS, Fraction(300, 1), Fraction(15, 1), 2)
        ed = DadosEdificacao(
            nome_edificacao="Torre Central",
            altura_total_m=Fraction(24, 1),
            tipo_escada=TipoEscada.ENCLAUSURADA_PROTEGIDA,
            possui_sprinklers=True,
            dados_degrau=deg,
            pavimentos=(p,),
        )
        self.assertEqual(ed.nome_edificacao, "Torre Central")
        self.assertEqual(len(ed.pavimentos), 1)

    def test_dados_edificacao_invalido(self) -> None:
        deg = DadosDegrau(Fraction(17, 100), Fraction(28, 100))
        with self.assertRaises(ValueError):
            DadosEdificacao(
                nome_edificacao="",
                altura_total_m=Fraction(24, 1),
                tipo_escada=TipoEscada.ENCLAUSURADA_PROTEGIDA,
                possui_sprinklers=True,
                dados_degrau=deg,
                pavimentos=(),
            )


if __name__ == "__main__":
    unittest.main()
