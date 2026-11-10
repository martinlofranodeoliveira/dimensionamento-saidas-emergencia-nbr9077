"""Testes do módulo codecs (JSON canônico RFC 8259 sem float)."""

import json
import unittest
from fractions import Fraction

from saidas_nbr9077.calculator import dimensionar_saidas_edificacao
from saidas_nbr9077.codecs import (
    carregar_dados_saidas_json,
    exportar_resultado_json,
    _para_fracao,
    _rejeitar_chaves_duplicadas,
    _rejeitar_float,
    _verificar_profundidade,
)
from saidas_nbr9077.models import DadosDegrau, DadosEdificacao, DadosPavimento, GrupoOcupacao, TipoEscada


class TestCodecs(unittest.TestCase):
    """Testes de conformidade e integridade do parser/serializer JSON canônico."""

    def test_para_fracao(self) -> None:
        self.assertEqual(_para_fracao(10), Fraction(10, 1))
        self.assertEqual(_para_fracao("12.5"), Fraction(25, 2))
        self.assertEqual(_para_fracao(Fraction(3, 4)), Fraction(3, 4))
        with self.assertRaises(ValueError):
            _para_fracao(12.5)  # type: ignore[arg-type]

    def test_rejeitar_float(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            _rejeitar_float("12.5")
        self.assertIn("Ponto flutuante", str(ctx.exception))

    def test_rejeitar_chaves_duplicadas(self) -> None:
        pares_validos = [("a", 1), ("b", 2)]
        self.assertEqual(_rejeitar_chaves_duplicadas(pares_validos), {"a": 1, "b": 2})

        pares_duplicados = [("a", 1), ("a", 2)]
        with self.assertRaises(ValueError) as ctx:
            _rejeitar_chaves_duplicadas(pares_duplicados)
        self.assertIn("Chave duplicada", str(ctx.exception))

    def test_verificar_profundidade(self) -> None:
        obj_ok: dict = {"a": {"b": {"c": [1, 2, 3]}}}
        _verificar_profundidade(obj_ok, profundidade=1, limite=5)

        # Objeto que excede a profundidade
        profundo: dict = {"k": 1}
        for _ in range(35):
            profundo = {"k": profundo}
        with self.assertRaises(ValueError) as ctx:
            _verificar_profundidade(profundo, profundidade=1, limite=32)
        self.assertIn("Profundidade", str(ctx.exception))

    def test_carregar_json_valido(self) -> None:
        json_txt = """{
            "nome_edificacao": "Edifício Comercial Alpha",
            "altura_total_m": "24",
            "tipo_escada": "enclausurada_protegida",
            "possui_sprinklers": true,
            "dados_degrau": {
                "altura_espelho_m": "0.175",
                "largura_piso_m": "0.28"
            },
            "pavimentos": [
                {
                    "nome_pavimento": "1º Pavimento",
                    "grupo_ocupacao": "D",
                    "area_liquida_m2": "400",
                    "distancia_percorrer_m": "22",
                    "quantidade_saidas_instaladas": 2
                }
            ]
        }"""
        edificacao = carregar_dados_saidas_json(json_txt)
        self.assertEqual(edificacao.nome_edificacao, "Edifício Comercial Alpha")
        self.assertEqual(edificacao.altura_total_m, Fraction(24, 1))
        self.assertTrue(edificacao.possui_sprinklers)
        self.assertEqual(len(edificacao.pavimentos), 1)
        self.assertEqual(edificacao.pavimentos[0].grupo_ocupacao, GrupoOcupacao.D_SERVICOS_PROFISSIONAIS)

    def test_rejeitar_bom(self) -> None:
        json_com_bom = "\ufeff" + '{"nome_edificacao": "Teste"}'
        with self.assertRaises(ValueError) as ctx:
            carregar_dados_saidas_json(json_com_bom)
        self.assertIn("Byte Order Mark", str(ctx.exception))

    def test_rejeitar_float_no_json(self) -> None:
        json_com_float = '{"nome_edificacao": "Teste", "altura_total_m": 12.5}'
        with self.assertRaises(ValueError) as ctx:
            carregar_dados_saidas_json(json_com_float)
        self.assertIn("Ponto flutuante", str(ctx.exception))

    def test_rejeitar_chave_duplicada_no_json(self) -> None:
        json_com_duplicata = '{"nome_edificacao": "A", "nome_edificacao": "B"}'
        with self.assertRaises(ValueError) as ctx:
            carregar_dados_saidas_json(json_com_duplicata)
        self.assertIn("Chave duplicada", str(ctx.exception))

    def test_rejeitar_estrutura_invalida(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            carregar_dados_saidas_json("[1, 2, 3]")
        self.assertIn("deve ser um objeto dicionário", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            carregar_dados_saidas_json('{"dados_degrau": "invalido"}')
        self.assertIn("dados_degrau' deve ser um dicionário", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            carregar_dados_saidas_json('{"pavimentos": "invalido"}')
        self.assertIn("pavimentos' deve ser uma lista", str(ctx.exception))

    def test_exportar_resultado_json(self) -> None:
        edificacao = DadosEdificacao(
            nome_edificacao="Hospital Central",
            altura_total_m=Fraction(15, 1),
            tipo_escada=TipoEscada.ENCLAUSURADA_PROTEGIDA,
            possui_sprinklers=False,
            dados_degrau=DadosDegrau(altura_espelho_m=Fraction(17, 100), largura_piso_m=Fraction(29, 100)),
            pavimentos=(
                DadosPavimento(
                    nome_pavimento="2º Pavimento",
                    grupo_ocupacao=GrupoOcupacao.H_SERVICOS_SAUDE,
                    area_liquida_m2=Fraction(500, 1),
                    distancia_percorrer_m=Fraction(20, 1),
                    quantidade_saidas_instaladas=2,
                ),
            ),
        )
        res = dimensionar_saidas_edificacao(edificacao)
        json_out = exportar_resultado_json(res)
        self.assertIsInstance(json_out, str)
        dados = json.loads(json_out)
        self.assertEqual(dados["norma"], "ABNT NBR 9077:2001")
        self.assertEqual(dados["nome_edificacao"], "Hospital Central")
        self.assertEqual(dados["tipo_escada"], "enclausurada_protegida")
        self.assertEqual(len(dados["pavimentos"]), 1)
        self.assertEqual(dados["pavimentos"][0]["largura_minima_portas_m"], "11/5")


if __name__ == "__main__":
    unittest.main()
