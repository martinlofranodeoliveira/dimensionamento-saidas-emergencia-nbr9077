"""Testes da interface de linha de comando (CLI) do pacote saidas_nbr9077."""

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from saidas_nbr9077 import __version__
from saidas_nbr9077.cli import main


class TestCLI(unittest.TestCase):
    """Bateria de testes funcionais da CLI."""

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.json_exemplo = os.path.join(self.tmpdir.name, "edificio_teste.json")
        conteudo = """{
            "nome_edificacao": "Torre Exemplo CLI",
            "altura_total_m": "24",
            "tipo_escada": "enclausurada_protegida",
            "possui_sprinklers": true,
            "dados_degrau": {
                "altura_espelho_m": "0.175",
                "largura_piso_m": "0.28"
            },
            "pavimentos": [
                {
                    "nome_pavimento": "Pavimento 1",
                    "grupo_ocupacao": "D",
                    "area_liquida_m2": "300",
                    "distancia_percorrer_m": "20",
                    "quantidade_saidas_instaladas": 2
                }
            ]
        }"""
        with open(self.json_exemplo, "w", encoding="utf-8") as f:
            f.write(conteudo)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_cli_versao(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out), self.assertRaises(SystemExit) as ctx:
            main(["--versao"])
        self.assertEqual(ctx.exception.code, 0)
        self.assertIn(__version__, out.getvalue())

    def test_cli_ajuda(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out), self.assertRaises(SystemExit) as ctx:
            main(["--ajuda"])
        self.assertEqual(ctx.exception.code, 0)
        self.assertIn("saidas-nbr9077", out.getvalue())
        self.assertIn("ABNT NBR 9077:2001", out.getvalue())

    def test_cli_sem_subcomando(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            ret = main([])
        self.assertEqual(ret, 0)
        self.assertIn("Subcomandos Disponíveis", out.getvalue())

    def test_cli_catalogo(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            ret = main(["catalogo"])
        self.assertEqual(ret, 0)
        saida = out.getvalue()
        self.assertIn("PARÂMETROS NORMATIVOS DA ABNT NBR 9077:2001", saida)
        self.assertIn("UNIDADE DE PASSAGEM", saida)
        self.assertIn("FÓRMULA DE BLONDEL", saida)

    def test_cli_gerar_exemplo_stdout(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            ret = main(["gerar-exemplo"])
        self.assertEqual(ret, 0)
        saida = out.getvalue()
        dados = json.loads(saida)
        self.assertIn("nome_edificacao", dados)
        self.assertIn("pavimentos", dados)

    def test_cli_gerar_exemplo_arquivo(self) -> None:
        caminho_out = os.path.join(self.tmpdir.name, "exemplo_gerado.json")
        out = io.StringIO()
        with redirect_stdout(out):
            ret = main(["gerar-exemplo", "--saida", caminho_out])
        self.assertEqual(ret, 0)
        self.assertTrue(os.path.exists(caminho_out))
        with open(caminho_out, "r", encoding="utf-8") as f:
            dados = json.load(f)
        self.assertIn("nome_edificacao", dados)

    def test_cli_calcular_texto(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            ret = main(["calcular", self.json_exemplo, "--formato", "texto"])
        self.assertEqual(ret, 0)
        saida = out.getvalue()
        self.assertIn("LOFRANO TECNOLOGIA", saida)
        self.assertIn("Torre Exemplo CLI", saida)

    def test_cli_calcular_json(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            ret = main(["calcular", self.json_exemplo, "--formato", "json"])
        self.assertEqual(ret, 0)
        dados = json.loads(out.getvalue())
        self.assertEqual(dados["nome_edificacao"], "Torre Exemplo CLI")
        self.assertEqual(dados["norma"], "ABNT NBR 9077:2001")

    def test_cli_calcular_csv(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            ret = main(["calcular", self.json_exemplo, "--formato", "csv"])
        self.assertEqual(ret, 0)
        saida = out.getvalue()
        self.assertIn("pavimento", saida)
        self.assertIn("Pavimento 1", saida)

    def test_cli_calcular_svg(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            ret = main(["calcular", self.json_exemplo, "--formato", "svg"])
        self.assertEqual(ret, 0)
        saida = out.getvalue()
        self.assertTrue(saida.strip().startswith("<svg"))
        self.assertTrue(saida.strip().endswith("</svg>"))

    def test_cli_calcular_com_pacote_zip(self) -> None:
        zip_out = os.path.join(self.tmpdir.name, "pacote_cli.zip")
        out = io.StringIO()
        with redirect_stdout(out):
            ret = main(["calcular", self.json_exemplo, "--pacote-zip", zip_out])
        self.assertEqual(ret, 0)
        self.assertTrue(os.path.exists(zip_out))

    def test_cli_calcular_arquivo_inexistente(self) -> None:
        err = io.StringIO()
        with redirect_stderr(err):
            ret = main(["calcular", "arquivo_que_nao_existe.json"])
        self.assertEqual(ret, 1)
        self.assertIn("Erro ao ler arquivo", err.getvalue())

    def test_cli_calcular_json_invalido(self) -> None:
        arquivo_ruim = os.path.join(self.tmpdir.name, "ruim.json")
        with open(arquivo_ruim, "w", encoding="utf-8") as f:
            f.write("{invalido: 123}")
        err = io.StringIO()
        with redirect_stderr(err):
            ret = main(["calcular", arquivo_ruim])
        self.assertEqual(ret, 1)
        self.assertIn("Erro ao processar JSON", err.getvalue())


if __name__ == "__main__":
    unittest.main()
