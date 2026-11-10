"""Gerador de painel técnico vetorial SVG para saídas de emergência NBR 9077:2001."""

from saidas_nbr9077.exporters import _fmt
from saidas_nbr9077.models import ResultadoDimensionamento


def gerar_painel_svg(res: ResultadoDimensionamento) -> str:
    """Gera painel vetorial SVG em alta resolução (1440x900) com esquema de saídas de emergência."""
    largura = 1440
    altura = 900

    linhas: list[str] = []
    linhas.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura} {altura}" width="{largura}" height="{altura}">')
    linhas.append('  <defs>')
    linhas.append('    <linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">')
    linhas.append('      <stop offset="0%" stop-color="#090d16" />')
    linhas.append('      <stop offset="100%" stop-color="#1e293b" />')
    linhas.append('    </linearGradient>')
    linhas.append('    <linearGradient id="degrauGrad" x1="0" y1="0" x2="1" y2="1">')
    linhas.append('      <stop offset="0%" stop-color="#3b82f6" />')
    linhas.append('      <stop offset="100%" stop-color="#1d4ed8" />')
    linhas.append('    </linearGradient>')
    linhas.append('    <linearGradient id="portaGrad" x1="0" y1="0" x2="0" y2="1">')
    linhas.append('      <stop offset="0%" stop-color="#ef4444" />')
    linhas.append('      <stop offset="100%" stop-color="#991b1b" />')
    linhas.append('    </linearGradient>')
    linhas.append('  </defs>')

    # Fundo geral
    linhas.append(f'  <rect width="{largura}" height="{altura}" fill="url(#bgGrad)" />')

    # Cabeçalho
    linhas.append('  <rect x="30" y="25" width="1380" height="75" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" />')
    linhas.append('  <text x="60" y="58" fill="#f8fafc" font-family="system-ui, -apple-system, sans-serif" font-size="20" font-weight="bold">LOFRANO TECNOLOGIA — ENGENHARIA DE SEGURANÇA CONTRA INCÊNDIO</text>')
    linhas.append('  <text x="60" y="82" fill="#38bdf8" font-family="system-ui, -apple-system, sans-serif" font-size="14">DIMENSIONAMENTO DE SAÍDAS DE EMERGÊNCIA EM EDIFÍCIOS — ABNT NBR 9077:2001</text>')
    linhas.append(f'  <text x="1380" y="70" text-anchor="end" fill="#94a3b8" font-family="monospace" font-size="13">Edificação: {res.nome_edificacao} | Altura: {_fmt(res.altura_total_m, 1)}m</text>')

    # Painel Esquerdo: Dados Consolidados e Ergonomia de Degraus
    linhas.append('  <g transform="translate(30, 120)">')
    linhas.append('    <rect width="360" height="745" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1" />')
    linhas.append('    <text x="20" y="35" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="16" font-weight="bold">PARÂMETROS GERAIS DO PROJETO</text>')
    linhas.append('    <line x1="20" y1="48" x2="340" y2="48" stroke="#334155" stroke-width="1" />')

    dados_painel_esq = [
        ("População Total", f"{res.populacao_total_edificacao} pessoas"),
        ("Tipologia da Escada", res.tipo_escada.value.upper()),
        ("Largura Mínima Padrão", "1,20 m (2 UP = 1,10m)"),
        ("Guarda-Corpo Mínimo", f"{_fmt(res.guarda_corpo.altura_minima_guarda_corpo_m, 2)} m"),
        ("Vão Máximo Barras Verticais", f"{_fmt(res.guarda_corpo.vao_maximo_barras_m, 2)} m (11 cm)"),
        ("Altura Corrimão", res.guarda_corpo.altura_corrimao_faixa_m),
    ]

    y_pos = 80
    for rotulo, val in dados_painel_esq:
        linhas.append(f'    <text x="20" y="{y_pos}" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12">{rotulo}</text>')
        linhas.append(f'    <text x="20" y="{y_pos + 20}" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="15" font-weight="bold">{val}</text>')
        y_pos += 50

    # Bloco de Detalhe Ergonômico de Degraus (Fórmula de Blondel)
    deg = res.degraus
    linhas.append('    <rect x="20" y="400" width="320" height="325" rx="6" fill="#0f172a" stroke="#475569" stroke-width="1" />')
    linhas.append('    <text x="35" y="425" fill="#facc15" font-family="system-ui, sans-serif" font-size="13" font-weight="bold">ERGONOMIA DE DEGRAUS (BLONDEL)</text>')

    # Desenho esquemático de um degrau com cotas
    linhas.append('    <g transform="translate(60, 450)">')
    linhas.append('      <path d="M 20 120 L 20 60 L 120 60 L 120 0 L 220 0" fill="none" stroke="#38bdf8" stroke-width="3" />')
    # Cota espelho (h)
    linhas.append('      <line x1="10" y1="60" x2="10" y2="120" stroke="#facc15" stroke-width="1.5" />')
    linhas.append(f'      <text x="5" y="95" text-anchor="end" fill="#facc15" font-family="system-ui, sans-serif" font-size="10" font-weight="bold">h={_fmt(deg.altura_espelho_m, 3)}m</text>')
    # Cota piso (b)
    linhas.append('      <line x1="20" y1="130" x2="120" y2="130" stroke="#4ade80" stroke-width="1.5" />')
    linhas.append(f'      <text x="70" y="145" text-anchor="middle" fill="#4ade80" font-family="system-ui, sans-serif" font-size="10" font-weight="bold">b={_fmt(deg.largura_piso_m, 3)}m</text>')
    linhas.append('    </g>')

    status_blondel = "CONFORME" if deg.conforme_geral else "NÃO CONFORME"
    cor_b = "#4ade80" if deg.conforme_geral else "#ef4444"
    linhas.append(f'    <text x="35" y="625" fill="{cor_b}" font-family="system-ui, sans-serif" font-size="12" font-weight="bold">• Blondel (2h+b): {_fmt(deg.valor_blondel_m, 3)} m [{status_blondel}]</text>')
    linhas.append('    <text x="35" y="645" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11">• Faixa Regulamentar: 0,63 m a 0,64 m</text>')
    linhas.append('    <text x="35" y="665" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11">• Espelho h: 0,16 m a 0,18 m</text>')
    linhas.append('    <text x="35" y="685" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11">• Piso b: no mínimo 0,27 m</text>')
    linhas.append('    <text x="35" y="705" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11">• Lance máx: 16 degraus ou 3,20 m</text>')
    linhas.append('  </g>')

    # Painel Central: Corte Esquemático da Rota de Fuga e Escada
    linhas.append('  <g transform="translate(410, 120)">')
    linhas.append('    <rect width="600" height="745" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1" />')
    linhas.append('    <text x="20" y="35" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="16" font-weight="bold">ESQUEMA DE ROTAS DE FUGA E CAIXA DE ESCADA</text>')
    linhas.append('    <line x1="20" y1="48" x2="580" y2="48" stroke="#334155" stroke-width="1" />')

    # Desenho de 4 pavimentos esquemáticos no corte
    num_exib = min(4, len(res.pavimentos))
    h_pav = 140
    y_base_corte = 70

    for i in range(num_exib):
        p_obj = res.pavimentos[i]
        yp = y_base_corte + i * h_pav

        # Pavimento e laje
        linhas.append(f'    <rect x="40" y="{yp}" width="360" height="{h_pav - 15}" fill="#0f172a" stroke="#334155" stroke-width="1" />')
        linhas.append(f'    <rect x="40" y="{yp + h_pav - 20}" width="360" height="6" fill="#475569" />')  # piso

        # Rótulo do pavimento
        linhas.append(f'    <text x="55" y="{yp + 25}" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="13" font-weight="bold">{p_obj.nome_pavimento}</text>')
        linhas.append(f'    <text x="55" y="{yp + 42}" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11">Grupo {p_obj.grupo_ocupacao.value} | População: {p_obj.populacao_calculada} pess. | Portas: {_fmt(p_obj.largura_minima_portas_m, 2)}m</text>')

        # Porta corta-fogo de acesso à escada
        x_porta = 370
        y_porta = yp + h_pav - 80
        linhas.append(f'    <rect x="{x_porta}" y="{y_porta}" width="18" height="60" rx="2" fill="url(#portaGrad)" />')
        linhas.append(f'    <circle cx="{x_porta + 13}" cy="{y_porta + 30}" r="2" fill="#facc15" />')  # maçaneta

        # Seta verde de fluxo de escape
        linhas.append(f'    <path d="M 280 {yp + 75} L 340 {yp + 75} L 330 {yp + 70} M 340 {yp + 75} L 330 {yp + 80}" stroke="#4ade80" stroke-width="2.5" fill="none" />')
        linhas.append(f'    <text x="300" y="{yp + 65}" text-anchor="middle" fill="#4ade80" font-family="system-ui, sans-serif" font-size="10" font-weight="bold">FUGA</text>')

    # Caixa vertical de escada à direita
    linhas.append(f'    <rect x="420" y="{y_base_corte}" width="150" height="{num_exib * h_pav - 15}" fill="#172554" stroke="#2563eb" stroke-width="1.5" />')
    linhas.append(f'    <text x="495" y="{y_base_corte + 25}" text-anchor="middle" fill="#93c5fd" font-family="system-ui, sans-serif" font-size="12" font-weight="bold">ESCADA ENCLAUSURADA</text>')

    # Desenho dos lances de escada na caixa
    for i in range(num_exib):
        yp = y_base_corte + i * h_pav
        linhas.append(f'    <line x1="430" y1="{yp + 35}" x2="560" y2="{yp + h_pav - 20}" stroke="#60a5fa" stroke-width="3" />')
        linhas.append(f'    <rect x="425" y="{yp + h_pav - 22}" width="140" height="5" fill="#3b82f6" />')

    # Legenda explicativa inferior
    linhas.append('    <rect x="40" y="650" width="530" height="75" rx="6" fill="#0f172a" stroke="#334155" stroke-width="1" />')
    linhas.append('    <text x="55" y="675" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="12" font-weight="bold">DIMENSIONAMENTO DA UNIDADE DE PASSAGEM (UP)</text>')
    linhas.append('    <text x="55" y="695" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11">• 1 UP = 0,55 m | Portas/Acessos: C = 100 pessoas/UP | Escadas: C = 60 (ou 45 em F).</text>')
    linhas.append('    <text x="55" y="712" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11">• Largura mínima regulamentar: 1,20 m (ou 2,20 m para hospitais e reunião > 300 pessoas).</text>')
    linhas.append('  </g>')

    # Painel Direito: Resumo e Tabela de Saídas por Pavimento
    linhas.append('  <g transform="translate(1030, 120)">')
    linhas.append('    <rect width="380" height="745" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1" />')
    linhas.append('    <text x="20" y="35" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="16" font-weight="bold">LARGURAS E CAMINHAMENTO</text>')
    linhas.append('    <line x1="20" y1="48" x2="360" y2="48" stroke="#334155" stroke-width="1" />')

    y_tab = 75
    for p in res.pavimentos:
        linhas.append(f'    <rect x="20" y="{y_tab}" width="340" height="110" rx="6" fill="#0f172a" stroke="#334155" stroke-width="1" />')
        linhas.append(f'    <text x="35" y="{y_tab + 22}" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="13" font-weight="bold">{p.nome_pavimento}</text>')
        linhas.append(f'    <text x="35" y="{y_tab + 40}" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11">Portas: {p.unidades_passagem_portas} UP ({_fmt(p.largura_minima_portas_m, 2)} m) | Escadas: {p.unidades_passagem_escadas} UP ({_fmt(p.largura_minima_escadas_m, 2)} m)</text>')
        status_d = "CONFORME" if p.conforme_distancia else "EXCEDE LIMITE"
        cor_d = "#4ade80" if p.conforme_distancia else "#ef4444"
        linhas.append(f'    <text x="35" y="{y_tab + 60}" fill="{cor_d}" font-family="system-ui, sans-serif" font-size="11">• Caminhamento: {_fmt(p.distancia_percorrer_m, 1)}m / Máx {_fmt(p.distancia_maxima_permitida_m, 1)}m [{status_d}]</text>')
        status_s = "CONFORME" if p.conforme_saidas else "INSUFICIENTE"
        cor_s = "#4ade80" if p.conforme_saidas else "#ef4444"
        linhas.append(f'    <text x="35" y="{y_tab + 80}" fill="{cor_s}" font-family="system-ui, sans-serif" font-size="11">• Saídas: {p.saidas_instaladas} instalada(s) / Mín {p.saidas_minimas_exigidas} [{status_s}]</text>')
        linhas.append(f'    <text x="35" y="{y_tab + 98}" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="10">Área: {_fmt(p.area_liquida_m2, 0)} m² | População: {p.populacao_calculada} pessoas</text>')
        y_tab += 120

    # Rodapé do painel direito
    linhas.append('    <rect x="20" y="650" width="340" height="75" rx="6" fill="#0f172a" stroke="#334155" stroke-width="1" />')
    linhas.append('    <text x="35" y="675" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="12" font-weight="bold">STATUS GLOBAL DE SAÍDAS</text>')
    status_cor = "#4ade80" if not res.alertas else "#facc15"
    status_msg = "SISTEMA CONFORME ABNT NBR 9077" if not res.alertas else f"{len(res.alertas)} ALERTA(S) REGISTRADO(S)"
    linhas.append(f'    <text x="35" y="698" fill="{status_cor}" font-family="system-ui, sans-serif" font-size="12" font-weight="bold">{status_msg}</text>')
    linhas.append('    <text x="35" y="715" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="10">Verificado via Lofrano Tecnologia</text>')
    linhas.append('  </g>')

    linhas.append('</svg>')
    return "\n".join(linhas)
