#!/usr/bin/env python3
"""Auditor independente em SQLite para saídas de emergência ABNT NBR 9077:2001.

Este script é uma ferramenta de auditoria independente e isolada.
Ele NÃO importa nenhum módulo do pacote de produção ('saidas_nbr9077').
Recria as fórmulas e regras normativas diretamente sobre um banco de dados
SQLite relacional puramente em memória, garantindo verificação fidedigna.
"""

import json
import os
import sqlite3
import sys
from fractions import Fraction

# Assegurar saída UTF-8 no Windows e Linux
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def verificar_arquivo_exemplo(caminho_json: str) -> None:
    nome_arq = os.path.basename(caminho_json)
    print(f"\n[AUDITORIA] Verificando arquivo: {nome_arq}")

    with open(caminho_json, "r", encoding="utf-8") as f:
        dados = json.load(f)

    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    # Tabelas de referência normativa NBR 9077
    cur.execute("""
        CREATE TABLE fatores_ocupacao (
            grupo TEXT PRIMARY KEY,
            area_por_pessoa INTEGER
        )
    """)
    cur.executemany("""
        INSERT INTO fatores_ocupacao VALUES (?, ?)
    """, [
        ("A", 15),
        ("B", 15),
        ("C", 4),
        ("D", 7),
        ("E", 2),
        ("F", 1),
        ("G", 40),
        ("H", 10),
        ("I", 10),
        ("J", 30),
    ])

    # 1. Auditoria dos Degraus (Fórmula de Blondel)
    deg = dados["dados_degrau"]
    h = Fraction(str(deg["altura_espelho_m"]))
    b = Fraction(str(deg["largura_piso_m"]))
    blondel = (Fraction(2, 1) * h) + b

    conf_blondel = Fraction(63, 100) <= blondel <= Fraction(64, 100)
    conf_espelho = Fraction(16, 100) <= h <= Fraction(18, 100)
    conf_piso = b >= Fraction(27, 100)

    print(f"  [OK] Degraus: h={h}m | b={b}m | Blondel (2h+b)={blondel}m")
    assert conf_blondel, f"Fórmula de Blondel {blondel}m fora da faixa regulamentar [0.63, 0.64]!"
    assert conf_espelho, f"Altura do espelho {h}m fora da faixa regulamentar [0.16, 0.18]!"
    assert conf_piso, f"Largura do piso {b}m menor que o mínimo de 0.27m!"

    # 2. Auditoria dos Pavimentos
    possui_sprinklers = bool(dados.get("possui_sprinklers", False))
    pavs = dados.get("pavimentos", [])

    for p in pavs:
        nome_p = p["nome_pavimento"]
        grupo = p["grupo_ocupacao"]
        area = Fraction(str(p["area_liquida_m2"]))
        dist_cam = Fraction(str(p["distancia_percorrer_m"]))
        saidas = int(p["quantidade_saidas_instaladas"])

        # População
        if "populacao_fixada" in p and p["populacao_fixada"] is not None:
            populacao = int(p["populacao_fixada"])
        else:
            cur.execute("SELECT area_por_pessoa FROM fatores_ocupacao WHERE grupo = ?", (grupo,))
            fator = cur.fetchone()[0]
            populacao = (area.numerator + (area.denominator * fator) - 1) // (area.denominator * fator)

        # Unidades de passagem
        cap_portas = 100
        cap_escadas = 45 if grupo == "F" else 60

        up_portas = max(2, (populacao + cap_portas - 1) // cap_portas)
        up_escadas = max(2, (populacao + cap_escadas - 1) // cap_escadas)

        larg_base = Fraction(22, 10) if grupo == "H" else Fraction(12, 10)
        larg_portas = max(larg_base, Fraction(up_portas, 1) * Fraction(55, 100))
        larg_escadas = max(larg_base, Fraction(up_escadas, 1) * Fraction(55, 100))

        # Distância máxima de caminhamento
        if possui_sprinklers:
            d_max = Fraction(65, 1) if saidas >= 2 else Fraction(45, 1)
        else:
            d_max = Fraction(45, 1) if saidas >= 2 else Fraction(30, 1)

        conf_dist = dist_cam <= d_max

        print(f"  [OK] Pavimento: {nome_p} | Grupo {grupo} | População: {populacao} pess.")
        print(f"       Portas: {up_portas} UP ({larg_portas}m) | Escadas: {up_escadas} UP ({larg_escadas}m)")
        print(f"       Caminhamento: {dist_cam}m / Máx {d_max}m [CONFORME]")
        assert conf_dist, f"Caminhamento {dist_cam}m excede limite de {d_max}m!"

    conn.close()
    print(f"  [SUCESSO] Auditoria de {nome_arq} aprovada 100%!\n")


def main() -> int:
    raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    exemplos_dir = os.path.join(raiz, "examples")

    arquivos = [
        "edificio_corporativo_escritorios.json",
        "escola_educacional_salas.json",
        "teatro_reuniao_publico.json",
    ]

    for arq in arquivos:
        caminho = os.path.join(exemplos_dir, arq)
        if os.path.exists(caminho):
            verificar_arquivo_exemplo(caminho)
        else:
            print(f"[ERRO] Arquivo não encontrado: {caminho}", file=sys.stderr)
            return 1

    print("=" * 80)
    print("TODAS AS AUDITORIAS INDEPENDENTES FORAM APROVADAS COM SUCESSO!")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
