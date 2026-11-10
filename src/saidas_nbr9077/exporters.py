"""Exportadores técnicos: memorial descritivo, CSV sanitizado e ZIP determinístico."""

import csv
import io
import os
import zipfile
from fractions import Fraction
from typing import Optional

from saidas_nbr9077.codecs import exportar_resultado_json
from saidas_nbr9077.models import ResultadoDimensionamento


def _fmt(val: Fraction, casas: int = 2) -> str:
    """Formata fração para string decimal com número fixo de casas sem IEEE float."""
    num = val.numerator
    den = val.denominator
    if den == 1:
        return f"{num}.0" if casas > 0 else str(num)
    inteiro = num // den
    resto = abs(num % den)
    fator = 10**casas
    frac_parte = (resto * fator + den // 2) // den
    return f"{inteiro}.{frac_parte:0{casas}d}"


def _sanitizar_campo_csv(val: str) -> str:
    """Sanitiza strings contra injeção de fórmulas de planilhas."""
    if val and val[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{val}"
    return val


def gerar_relatorio_texto(res: ResultadoDimensionamento) -> str:
    """Gera memorial descritivo técnico detalhado de saídas de emergência NBR 9077."""
    linhas: list[str] = []
    w = 80
    linhas.append("=" * w)
    linhas.append("    LOFRANO TECNOLOGIA - ENGENHARIA DE SEGURANÇA CONTRA INCÊNDIO")
    linhas.append("    SAÍDAS DE EMERGÊNCIA EM EDIFÍCIOS - ABNT NBR 9077:2001")
    linhas.append("=" * w)
    linhas.append(f"Edificação: {res.nome_edificacao}")
    linhas.append(f"Altura:     {_fmt(res.altura_total_m, 1)} m")
    linhas.append(f"Escada:     {res.tipo_escada.value.upper()}")
    linhas.append(f"População:  {res.populacao_total_edificacao} pessoa(s) no total")
    linhas.append("-" * w)

    linhas.append("1. ERGONOMIA DE DEGRAUS E ESCADAS (FÓRMULA DE BLONDEL)")
    deg = res.degraus
    linhas.append(f"  - Altura do Espelho (h):       {_fmt(deg.altura_espelho_m, 3)} m (16,0 cm a 18,0 cm) [{'CONFORME' if deg.conforme_espelho else 'NÃO CONFORME'}]")
    linhas.append(f"  - Largura do Piso (b):         {_fmt(deg.largura_piso_m, 3)} m (Mín: 27,0 cm) [{'CONFORME' if deg.conforme_piso else 'NÃO CONFORME'}]")
    linhas.append(f"  - Fórmula de Blondel (2h + b): {_fmt(deg.valor_blondel_m, 3)} m (Faixa: 0,63 m a 0,64 m) [{'CONFORME' if deg.conforme_blondel else 'NÃO CONFORME'}]")
    linhas.append(f"  - Comprimento Mínimo Patamar:  {_fmt(deg.patamar_minimo_m, 2)} m")
    linhas.append("-" * w)

    linhas.append("2. GUARDA-CORPOS E CORRIMÃOS")
    gc = res.guarda_corpo
    linhas.append(f"  - Altura Mínima Guarda-Corpo:  {_fmt(gc.altura_minima_guarda_corpo_m, 2)} m")
    linhas.append(f"  - Vão Livre Máximo em Barras:  {_fmt(gc.vao_maximo_barras_m, 2)} m (11,0 cm vertical)")
    linhas.append(f"  - Altura Regulamentar Corrimão: {gc.altura_corrimao_faixa_m}")
    linhas.append(f"  - Exigência Corrimão Central:   {'SIM (Largura > 2,20m)' if gc.exige_corrimao_central else 'NÃO'}")
    linhas.append("-" * w)

    linhas.append("3. DIMENSIONAMENTO DE SAÍDAS POR PAVIMENTO")
    for idx, p in enumerate(res.pavimentos, start=1):
        linhas.append(f"  [{idx}] {p.nome_pavimento}:")
        linhas.append(f"      - Ocupação: Grupo {p.grupo_ocupacao.value} | Área Líquida: {_fmt(p.area_liquida_m2, 1)} m²")
        linhas.append(f"      - População de Cálculo: {p.populacao_calculada} pessoa(s)")
        linhas.append(f"      - Portas/Acessos: {p.unidades_passagem_portas} UP -> Largura Mínima: {_fmt(p.largura_minima_portas_m, 2)} m")
        linhas.append(f"      - Escadas/Rampas: {p.unidades_passagem_escadas} UP -> Largura Mínima: {_fmt(p.largura_minima_escadas_m, 2)} m")
        status_d = "CONFORME" if p.conforme_distancia else "NÃO CONFORME"
        linhas.append(f"      - Caminhamento: {_fmt(p.distancia_percorrer_m, 1)} m (Máx: {_fmt(p.distancia_maxima_permitida_m, 1)} m) [{status_d}]")
        status_s = "CONFORME" if p.conforme_saidas else "NÃO CONFORME"
        linhas.append(f"      - Saídas: {p.saidas_instaladas} instalada(s) (Mín: {p.saidas_minimas_exigidas}) [{status_s}]")
        linhas.append("-" * w)

    if res.alertas:
        linhas.append("4. ALERTAS E INCONFORMIDADES REGISTRADAS")
        for alerta in res.alertas:
            linhas.append(f"  [ALERTA] {alerta}")
        linhas.append("-" * w)

    linhas.append("5. DIRETRIZES TÉCNICAS E RECOMENDAÇÕES NORMATIVAS")
    for rec in res.recomendacoes:
        linhas.append(f"  * {rec}")
    linhas.append("=" * w)
    linhas.append("Emitido via Lofrano Tecnologia - Conforme ABNT NBR 9077:2001")
    linhas.append("=" * w)

    return "\n".join(linhas)


def gerar_csv_sanitizado(res: ResultadoDimensionamento) -> str:
    """Gera resumo tabular estruturado em CSV sanitizado contra injeção de fórmulas."""
    saida = io.StringIO()
    writer = csv.writer(saida, delimiter=";", lineterminator="\n")

    writer.writerow([
        _sanitizar_campo_csv("pavimento"),
        _sanitizar_campo_csv("grupo_ocupacao"),
        _sanitizar_campo_csv("area_liquida_m2"),
        _sanitizar_campo_csv("populacao"),
        _sanitizar_campo_csv("up_portas"),
        _sanitizar_campo_csv("largura_portas_m"),
        _sanitizar_campo_csv("up_escadas"),
        _sanitizar_campo_csv("largura_escadas_m"),
        _sanitizar_campo_csv("distancia_m"),
        _sanitizar_campo_csv("dist_max_m"),
        _sanitizar_campo_csv("saidas_instaladas"),
        _sanitizar_campo_csv("saidas_minimas"),
    ])

    for p in res.pavimentos:
        writer.writerow([
            _sanitizar_campo_csv(p.nome_pavimento),
            p.grupo_ocupacao.value,
            _fmt(p.area_liquida_m2, 1),
            str(p.populacao_calculada),
            str(p.unidades_passagem_portas),
            _fmt(p.largura_minima_portas_m, 2),
            str(p.unidades_passagem_escadas),
            _fmt(p.largura_minima_escadas_m, 2),
            _fmt(p.distancia_percorrer_m, 1),
            _fmt(p.distancia_maxima_permitida_m, 1),
            str(p.saidas_instaladas),
            str(p.saidas_minimas_exigidas),
        ])

    return saida.getvalue()


def gerar_pacote_zip(res: ResultadoDimensionamento, caminho_zip: str, svg_conteudo: Optional[str] = None) -> None:
    """Gera pacote determinístico ZIP com O_EXCL, evitando sobrescrita acidental."""
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0)
    fd = os.open(caminho_zip, flags, 0o644)
    fixed_time = (2026, 1, 1, 0, 0, 0)

    try:
        with open(fd, "wb", closefd=True) as f_out:
            with zipfile.ZipFile(f_out, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
                # 1. Memorial descritivo em texto
                txt = gerar_relatorio_texto(res).encode("utf-8")
                zi_txt = zipfile.ZipInfo(filename="memorial_descritivo.txt", date_time=fixed_time)
                zf.writestr(zi_txt, txt)

                # 2. Dados em JSON canônico
                js = exportar_resultado_json(res).encode("utf-8")
                zi_js = zipfile.ZipInfo(filename="dados_saidas.json", date_time=fixed_time)
                zf.writestr(zi_js, js)

                # 3. Planilha CSV sanitizada
                csv_data = gerar_csv_sanitizado(res).encode("utf-8")
                zi_csv = zipfile.ZipInfo(filename="resumo_saidas.csv", date_time=fixed_time)
                zf.writestr(zi_csv, csv_data)

                # 4. Painel vetorial SVG se disponível
                if svg_conteudo:
                    svg_bytes = svg_conteudo.encode("utf-8")
                    zi_svg = zipfile.ZipInfo(filename="painel_esquematico.svg", date_time=fixed_time)
                    zf.writestr(zi_svg, svg_bytes)
    except Exception:
        if os.path.exists(caminho_zip):
            try:
                os.remove(caminho_zip)
            except OSError:
                pass
        raise
