"""Interface de Linha de Comando (CLI) para saídas de emergência NBR 9077:2001."""

import argparse
import sys
from typing import Sequence

from saidas_nbr9077 import __version__
from saidas_nbr9077.calculator import dimensionar_saidas_edificacao
from saidas_nbr9077.codecs import carregar_dados_saidas_json, exportar_resultado_json
from saidas_nbr9077.exporters import gerar_csv_sanitizado, gerar_pacote_zip, gerar_relatorio_texto
from saidas_nbr9077.svg_generator import gerar_painel_svg


def _comando_calcular(args: argparse.Namespace) -> int:
    try:
        with open(args.arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read()
    except Exception as err:
        print(f"Erro ao ler arquivo de entrada: {err}", file=sys.stderr)
        return 1

    try:
        dados = carregar_dados_saidas_json(conteudo)
    except Exception as err:
        print(f"Erro ao processar JSON: {err}", file=sys.stderr)
        return 1

    resultado = dimensionar_saidas_edificacao(dados)

    # Geração do pacote ZIP determinístico se solicitado
    if args.pacote_zip:
        try:
            svg_conteudo = gerar_painel_svg(resultado)
            gerar_pacote_zip(resultado, args.pacote_zip, svg_conteudo)
            print(f"[ZIP] Pacote determinístico gerado com sucesso em '{args.pacote_zip}'")
        except Exception as err:
            print(f"Erro ao gerar pacote ZIP: {err}", file=sys.stderr)
            return 1

    # Formatação da saída solicitada
    formato = args.formato.lower()
    if formato == "json":
        saida_str = exportar_resultado_json(resultado)
    elif formato == "csv":
        saida_str = gerar_csv_sanitizado(resultado)
    elif formato == "svg":
        saida_str = gerar_painel_svg(resultado)
    else:
        saida_str = gerar_relatorio_texto(resultado)

    if args.saida:
        try:
            with open(args.saida, "w", encoding="utf-8") as f:
                f.write(saida_str)
            print(f"[OK] Saída ({formato}) salva com sucesso em '{args.saida}'")
        except Exception as err:
            print(f"Erro ao salvar arquivo de saída: {err}", file=sys.stderr)
            return 1
    else:
        print(saida_str)

    return 0


def _comando_catalogo(args: argparse.Namespace) -> int:
    print("=" * 80)
    print("    LOFRANO TECNOLOGIA - PARÂMETROS NORMATIVOS DA ABNT NBR 9077:2001")
    print("=" * 80)
    print("1. UNIDADE DE PASSAGEM (UP = 0,55 m) E CAPACIDADES 'C'")
    print("  - Portas e acessos horizontais: C = 100 pessoas / UP")
    print("  - Escadas e rampas em geral:    C = 60 pessoas / UP")
    print("  - Escadas em locais de reunião: C = 45 pessoas / UP (Grupo F)")
    print("-" * 80)
    print("2. LARGURAS MÍNIMAS REGULAMENTARES")
    print("  - Padrão geral de edificações:  1,20 m (2 UP = 1,10 m arredondado normativamente)")
    print("  - Hospitais (circulação leitos): 2,20 m")
    print("  - Locais de reunião de público: 2,20 m (se população > 300 pessoas)")
    print("-" * 80)
    print("3. ERGONOMIA DE DEGRAUS (FÓRMULA DE BLONDEL)")
    print("  - 63 cm <= (2h + b) <= 64 cm")
    print("  - Altura de espelho (h): 16,0 cm a 18,0 cm")
    print("  - Largura de piso (b):   mínimo de 27,0 cm")
    print("  - Degraus por lance:     mínimo 3, máximo 16 degraus (patamar a cada 3,20 m)")
    print("-" * 80)
    print("4. GUARDA-CORPOS E CORRIMÃOS")
    print("  - Guarda-corpo: h >= 1,05 m (desnível <= 12m) ou h >= 1,30 m (desnível > 12m)")
    print("  - Vão livre máximo entre barras verticais: 11,0 cm (proibidas barras horizontais)")
    print("  - Corrimão: altura entre 0,80 m e 0,92 m (exige central se escada > 2,20 m)")
    print("=" * 80)
    return 0


def _comando_gerar_exemplo(args: argparse.Namespace) -> int:
    exemplo_json = """{
  "nome_edificacao": "Edifício Comercial Rocha Corporate",
  "altura_total_m": 28.0,
  "tipo_escada": "enclausurada_protegida",
  "possui_sprinklers": true,
  "dados_degrau": {
    "altura_espelho_m": "0.175",
    "largura_piso_m": "0.285"
  },
  "pavimentos": [
    {
      "nome_pavimento": "Térreo - Hall e Acesso Principal",
      "grupo_ocupacao": "D",
      "area_liquida_m2": 450,
      "distancia_percorrer_m": 22,
      "quantidade_saidas_instaladas": 2
    },
    {
      "nome_pavimento": "1º ao 8º Pavimento Tipo",
      "grupo_ocupacao": "D",
      "area_liquida_m2": 380,
      "distancia_percorrer_m": 28,
      "quantidade_saidas_instaladas": 2
    }
  ]
}
"""
    if args.saida:
        try:
            with open(args.saida, "w", encoding="utf-8") as f:
                f.write(exemplo_json)
            print(f"[OK] Modelo de exemplo gravado em '{args.saida}'")
        except Exception as err:
            print(f"Erro ao gravar arquivo de exemplo: {err}", file=sys.stderr)
            return 1
    else:
        print(exemplo_json)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Ponto de entrada principal da CLI."""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="saidas-nbr9077",
        description="Dimensionamento de Saídas de Emergência em Edifícios (ABNT NBR 9077:2001) - Lofrano Tecnologia",
        add_help=False,
    )

    parser.add_argument("-h", "--help", "--ajuda", action="help", help="Exibe esta mensagem de ajuda e encerra.")
    parser.add_argument("-v", "--version", "--versao", action="version", version=f"%(prog)s {__version__}", help="Exibe a versão do programa.")

    subparsers = parser.add_subparsers(dest="subcomando", title="Subcomandos Disponíveis")

    # Subcomando 'calcular'
    parser_calc = subparsers.add_parser("calcular", help="Dimensiona as saídas de emergência a partir de arquivo JSON.")
    parser_calc.add_argument("arquivo", help="Caminho do arquivo JSON de entrada.")
    parser_calc.add_argument(
        "--formato",
        choices=["texto", "json", "csv", "svg"],
        default="texto",
        help="Formato de saída dos resultados (padrão: texto).",
    )
    parser_calc.add_argument("--saida", help="Arquivo de destino para salvar a saída.")
    parser_calc.add_argument("--pacote-zip", help="Gera pacote ZIP determinístico completo no caminho especificado.")

    # Subcomando 'catalogo'
    subparsers.add_parser("catalogo", help="Exibe o catálogo de referências e critérios normativos da NBR 9077:2001.")

    # Subcomando 'gerar-exemplo'
    parser_ex = subparsers.add_parser("gerar-exemplo", help="Gera arquivo JSON modelo de exemplo para preenchimento.")
    parser_ex.add_argument("--saida", help="Arquivo de destino para gravar o JSON de exemplo.")

    args = parser.parse_args(argv)

    if not args.subcomando:
        parser.print_help()
        return 0

    if args.subcomando == "calcular":
        return _comando_calcular(args)
    elif args.subcomando == "catalogo":
        return _comando_catalogo(args)
    elif args.subcomando == "gerar-exemplo":
        return _comando_gerar_exemplo(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
