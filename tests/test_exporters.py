"""Testes dos exportadores (memorial texto, CSV sanitizado e pacote ZIP determinístico)."""

import os
import tempfile
import unittest
import zipfile
from fractions import Fraction

from saidas_nbr9077.calculator import dimensionar_saidas_edificacao
from saidas_nbr9077.exporters import (
    _fmt,
    _sanitizar_campo_csv,
    gerar_csv_sanitizado,
    gerar_pacote_zip,
    gerar_relatorio_texto,
)
from saidas_nbr9077.models import (
    DadosDegrau,
    DadosEdificacao,
    DadosPavimento,
    GrupoOcupacao,
    TipoEscada,
)


class TestExporters(unittest.TestCase):
    """Testes dos geradores de relatórios e exportação determinística."""

    def setUp(self) -> None:
        self.edificacao = DadosEdificacao(
            nome_edificacao="Empresarial Horizonte",
            altura_total_m=Fraction(18, 1),
            tipo_escada=TipoEscada.ENCLAUSURADA_FUMACA,
            possui_sprinklers=True,
            dados_degrau=DadosDegrau(altura_espelho_m=Fraction(17, 100), largura_piso_m=Fraction(29, 100)),
            pavimentos=(
                DadosPavimento(
                    nome_pavimento="Tipo 1 ao 5",
                    grupo_ocupacao=GrupoOcupacao.D_SERVICOS_PROFISSIONAIS,
                    area_liquida_m2=Fraction(450, 1),
                    distancia_percorrer_m=Fraction(25, 1),
                    quantidade_saidas_instaladas=2,
                ),
            ),
        )
        self.resultado = dimensionar_saidas_edificacao(self.edificacao)

    def test_fmt_fracao(self) -> None:
        self.assertEqual(_fmt(Fraction(10, 1), 2), "10.0")
        self.assertEqual(_fmt(Fraction(1, 2), 2), "0.50")
        self.assertEqual(_fmt(Fraction(11, 10), 2), "1.10")
        self.assertEqual(_fmt(Fraction(22, 10), 2), "2.20")
        self.assertEqual(_fmt(Fraction(15, 1), 0), "15")

    def test_sanitizar_campo_csv(self) -> None:
        self.assertEqual(_sanitizar_campo_csv("Normal"), "Normal")
        self.assertEqual(_sanitizar_campo_csv("=1+1"), "'=1+1")
        self.assertEqual(_sanitizar_campo_csv("+SUM(A1:A5)"), "'+SUM(A1:A5)")
        self.assertEqual(_sanitizar_campo_csv("-123"), "'-123")
        self.assertEqual(_sanitizar_campo_csv("@CMD"), "'@CMD")
        self.assertEqual(_sanitizar_campo_csv("\ttab"), "'\ttab")
        self.assertEqual(_sanitizar_campo_csv("\rcarriage"), "'\rcarriage")
        self.assertEqual(_sanitizar_campo_csv(""), "")

    def test_gerar_relatorio_texto(self) -> None:
        texto = gerar_relatorio_texto(self.resultado)
        self.assertIn("LOFRANO TECNOLOGIA", texto)
        self.assertIn("ABNT NBR 9077:2001", texto)
        self.assertIn("Empresarial Horizonte", texto)
        self.assertIn("FÓRMULA DE BLONDEL", texto)
        self.assertIn("0,63 m a 0,64 m", texto)
        self.assertIn("Tipo 1 ao 5", texto)
        self.assertIn("CONFORME", texto)

    def test_gerar_csv_sanitizado(self) -> None:
        csv_txt = gerar_csv_sanitizado(self.resultado)
        linhas = csv_txt.strip().split("\n")
        self.assertGreaterEqual(len(linhas), 2)
        cabecalho = linhas[0]
        self.assertIn("pavimento", cabecalho)
        self.assertIn("populacao", cabecalho)
        self.assertIn("largura_portas_m", cabecalho)
        self.assertIn("Tipo 1 ao 5", linhas[1])

    def test_gerar_pacote_zip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_zip = os.path.join(tmpdir, "pacote_teste.zip")
            svg_dummy = "<svg><text>Teste</text></svg>"
            gerar_pacote_zip(self.resultado, caminho_zip, svg_conteudo=svg_dummy)

            self.assertTrue(os.path.exists(caminho_zip))
            with zipfile.ZipFile(caminho_zip, "r") as zf:
                nomes = zf.namelist()
                self.assertIn("memorial_descritivo.txt", nomes)
                self.assertIn("dados_saidas.json", nomes)
                self.assertIn("resumo_saidas.csv", nomes)
                self.assertIn("painel_esquematico.svg", nomes)

                # Verificar timestamp determinístico
                for info in zf.infolist():
                    self.assertEqual(info.date_time, (2026, 1, 1, 0, 0, 0))


if __name__ == "__main__":
    unittest.main()
