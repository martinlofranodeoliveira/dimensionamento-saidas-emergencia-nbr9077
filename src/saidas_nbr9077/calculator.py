"""Motor de cálculo normativo para dimensionamento de saídas de emergência NBR 9077:2001."""

from fractions import Fraction
from saidas_nbr9077.constants import (
    ALTURA_CORRIMAO_MAXIMA_M,
    ALTURA_CORRIMAO_MINIMA_M,
    ALTURA_ESPELHO_MAXIMA_M,
    ALTURA_ESPELHO_MINIMA_M,
    ALTURA_MINIMA_GUARDA_CORPO_ALTA_M,
    ALTURA_MINIMA_GUARDA_CORPO_BAIXA_M,
    BLONDEL_MAXIMO_M,
    BLONDEL_MINIMO_M,
    CAPACIDADE_UP_ESCADAS_GERAL,
    CAPACIDADE_UP_ESCADAS_REUNIAO_F,
    CAPACIDADE_UP_PORTAS_ACESSOS,
    DISTANCIA_MAX_MULTIPLA_COM_SPRINKLERS_M,
    DISTANCIA_MAX_MULTIPLA_SEM_SPRINKLERS_M,
    DISTANCIA_MAX_UNICA_COM_SPRINKLERS_M,
    DISTANCIA_MAX_UNICA_SEM_SPRINKLERS_M,
    LARGURA_LIMITE_CORRIMAO_CENTRAL_M,
    LARGURA_MINIMA_HOSPITAIS_LEITOS_M,
    LARGURA_MINIMA_SAIDA_GERAL_M,
    LARGURA_PISO_MINIMA_M,
    LARGURA_UNIDADE_PASSAGEM_M,
    VAO_MAXIMO_BARRAS_VERTICAIS_M,
)
from saidas_nbr9077.models import (
    DadosDegrau,
    DadosEdificacao,
    DadosPavimento,
    GrupoOcupacao,
    ResultadoDegraus,
    ResultadoDimensionamento,
    ResultadoGuardaCorpo,
    ResultadoPavimento,
)


def _teto_fracao(frac: Fraction) -> int:
    """Calcula o teto inteiro exato de uma fração sem IEEE float."""
    if frac.denominator == 1:
        return frac.numerator
    if frac.numerator > 0:
        return (frac.numerator // frac.denominator) + 1
    return frac.numerator // frac.denominator


def obter_fator_area_por_pessoa(grupo: GrupoOcupacao) -> Fraction:
    """Retorna o coeficiente de área em m² por pessoa conforme Tabela 1 da NBR 9077."""
    fatores = {
        GrupoOcupacao.A_RESIDENCIAL: Fraction(15, 1),             # 1 pessoa a cada 15 m² de dormitório
        GrupoOcupacao.B_HOSPEDAGEM: Fraction(15, 1),              # 1 pessoa a cada 15 m²
        GrupoOcupacao.C_COMERCIAL: Fraction(4, 1),                # 1 pessoa a cada 4 m²
        GrupoOcupacao.D_SERVICOS_PROFISSIONAIS: Fraction(7, 1),   # 1 pessoa a cada 7 m² (escritórios)
        GrupoOcupacao.E_EDUCACIONAL: Fraction(2, 1),              # 1 pessoa a cada 2 m²
        GrupoOcupacao.F_REUNIAO_PUBLICO: Fraction(1, 1),          # 1 pessoa a cada 1 m² (reunião geral/restaurantes)
        GrupoOcupacao.G_GARAGEM: Fraction(40, 1),                 # 1 pessoa a cada 40 m²
        GrupoOcupacao.H_SERVICOS_SAUDE: Fraction(10, 1),          # 1 pessoa a cada 10 m²
        GrupoOcupacao.I_INDUSTRIAL: Fraction(10, 1),              # 1 pessoa a cada 10 m²
        GrupoOcupacao.J_DEPOSITO: Fraction(30, 1),                # 1 pessoa a cada 30 m²
    }
    return fatores.get(grupo, Fraction(7, 1))


def verificar_degraus_blondel(dados: DadosDegrau) -> ResultadoDegraus:
    """Valida o dimensionamento dos degraus segundo a Fórmula de Blondel (63cm <= 2h + b <= 64cm)."""
    h = dados.altura_espelho_m
    b = dados.largura_piso_m
    blondel = (Fraction(2, 1) * h) + b

    conf_blondel = BLONDEL_MINIMO_M <= blondel <= BLONDEL_MAXIMO_M
    conf_espelho = ALTURA_ESPELHO_MINIMA_M <= h <= ALTURA_ESPELHO_MAXIMA_M
    conf_piso = b >= LARGURA_PISO_MINIMA_M
    conf_geral = conf_blondel and conf_espelho and conf_piso

    # Patamar mínimo igual à largura mínima regulamentar
    patamar_min = LARGURA_MINIMA_SAIDA_GERAL_M

    return ResultadoDegraus(
        altura_espelho_m=h,
        largura_piso_m=b,
        valor_blondel_m=blondel,
        conforme_blondel=conf_blondel,
        conforme_espelho=conf_espelho,
        conforme_piso=conf_piso,
        conforme_geral=conf_geral,
        patamar_minimo_m=patamar_min,
    )


def dimensionar_pavimento(
    pav: DadosPavimento,
    possui_sprinklers: bool,
    alertas: list[str] | None = None,
) -> ResultadoPavimento:
    """Calcula a população, unidades de passagem, larguras e distâncias de um pavimento."""
    if alertas is None:
        alertas = []

    # 1. População de cálculo
    if pav.populacao_fixada is not None:
        populacao = pav.populacao_fixada
    else:
        fator_area = obter_fator_area_por_pessoa(pav.grupo_ocupacao)
        populacao = _teto_fracao(pav.area_liquida_m2 / fator_area)

    # 2. Capacidade da UP e Unidades de Passagem
    cap_portas = CAPACIDADE_UP_PORTAS_ACESSOS  # 100
    if pav.grupo_ocupacao == GrupoOcupacao.F_REUNIAO_PUBLICO:
        cap_escadas = CAPACIDADE_UP_ESCADAS_REUNIAO_F  # 45
    else:
        cap_escadas = CAPACIDADE_UP_ESCADAS_GERAL  # 60

    up_portas_calc = _teto_fracao(Fraction(populacao, cap_portas))
    up_portas = max(2, up_portas_calc)

    up_escadas_calc = _teto_fracao(Fraction(populacao, cap_escadas))
    up_escadas = max(2, up_escadas_calc)

    # 3. Larguras mínimas requeridas em metros
    if pav.grupo_ocupacao == GrupoOcupacao.H_SERVICOS_SAUDE:
        largura_min_base = LARGURA_MINIMA_HOSPITAIS_LEITOS_M  # 2.20 m
    else:
        largura_min_base = LARGURA_MINIMA_SAIDA_GERAL_M       # 1.20 m

    largura_portas_m = max(largura_min_base, Fraction(up_portas, 1) * LARGURA_UNIDADE_PASSAGEM_M)
    largura_escadas_m = max(largura_min_base, Fraction(up_escadas, 1) * LARGURA_UNIDADE_PASSAGEM_M)

    # 4. Número de saídas mínimas exigidas
    if populacao > 100 or pav.grupo_ocupacao in (GrupoOcupacao.F_REUNIAO_PUBLICO, GrupoOcupacao.H_SERVICOS_SAUDE):
        saidas_minimas = 2
    else:
        saidas_minimas = 1

    conforme_saidas = pav.quantidade_saidas_instaladas >= saidas_minimas
    if not conforme_saidas:
        alertas.append(
            f"Pavimento '{pav.nome_pavimento}': população de {populacao} pessoas exige no mínimo {saidas_minimas} "
            f"saídas distintas, porém apenas {pav.quantidade_saidas_instaladas} foi informada."
        )

    # 5. Distância máxima a percorrer
    multiplas_saidas = pav.quantidade_saidas_instaladas >= 2
    if possui_sprinklers:
        dist_max_permitida = (
            DISTANCIA_MAX_MULTIPLA_COM_SPRINKLERS_M if multiplas_saidas else DISTANCIA_MAX_UNICA_COM_SPRINKLERS_M
        )
    else:
        dist_max_permitida = (
            DISTANCIA_MAX_MULTIPLA_SEM_SPRINKLERS_M if multiplas_saidas else DISTANCIA_MAX_UNICA_SEM_SPRINKLERS_M
        )

    conforme_distancia = pav.distancia_percorrer_m <= dist_max_permitida
    if not conforme_distancia:
        alertas.append(
            f"Pavimento '{pav.nome_pavimento}': distância a percorrer de {pav.distancia_percorrer_m}m excede "
            f"o limite normativo de {dist_max_permitida}m para a configuração adotada."
        )

    return ResultadoPavimento(
        nome_pavimento=pav.nome_pavimento,
        grupo_ocupacao=pav.grupo_ocupacao,
        area_liquida_m2=pav.area_liquida_m2,
        populacao_calculada=populacao,
        unidades_passagem_portas=up_portas,
        largura_minima_portas_m=largura_portas_m,
        unidades_passagem_escadas=up_escadas,
        largura_minima_escadas_m=largura_escadas_m,
        distancia_percorrer_m=pav.distancia_percorrer_m,
        distancia_maxima_permitida_m=dist_max_permitida,
        conforme_distancia=conforme_distancia,
        saidas_minimas_exigidas=saidas_minimas,
        saidas_instaladas=pav.quantidade_saidas_instaladas,
        conforme_saidas=conforme_saidas,
    )


def dimensionar_saidas_edificacao(dados: DadosEdificacao) -> ResultadoDimensionamento:
    """Realiza o dimensionamento técnico completo das saídas de emergência NBR 9077:2001."""
    alertas: list[str] = []
    recomendacoes: list[str] = []

    # 1. Verificação ergonômica de degraus
    res_degraus = verificar_degraus_blondel(dados.dados_degrau)
    if not res_degraus.conforme_geral:
        if not res_degraus.conforme_blondel:
            alertas.append(
                f"Degraus: Fórmula de Blondel ({res_degraus.valor_blondel_m}m) fora da faixa regulamentar de 0,63 m a 0,64 m."
            )
        if not res_degraus.conforme_espelho:
            alertas.append(
                f"Degraus: Altura de espelho ({res_degraus.altura_espelho_m}m) fora dos limites normativos (0,16 m a 0,18 m)."
            )
        if not res_degraus.conforme_piso:
            alertas.append(
                f"Degraus: Largura de piso ({res_degraus.largura_piso_m}m) inferior ao mínimo de 0,27 m."
            )

    # 2. Guarda-corpos e corrimãos
    if dados.altura_total_m > Fraction(12, 1):
        alt_gc = ALTURA_MINIMA_GUARDA_CORPO_ALTA_M  # 1.30 m
    else:
        alt_gc = ALTURA_MINIMA_GUARDA_CORPO_BAIXA_M  # 1.05 m

    # 3. Dimensionamento dos pavimentos
    res_pavimentos: list[ResultadoPavimento] = []
    populacao_total = 0
    maior_largura_escada = Fraction(12, 10)

    for p in dados.pavimentos:
        rp = dimensionar_pavimento(p, dados.possui_sprinklers, alertas)
        res_pavimentos.append(rp)
        populacao_total += rp.populacao_calculada
        if rp.largura_minima_escadas_m > maior_largura_escada:
            maior_largura_escada = rp.largura_minima_escadas_m

    exige_corrimao_central = maior_largura_escada > LARGURA_LIMITE_CORRIMAO_CENTRAL_M

    res_gc = ResultadoGuardaCorpo(
        altura_minima_guarda_corpo_m=alt_gc,
        vao_maximo_barras_m=VAO_MAXIMO_BARRAS_VERTICAIS_M,
        altura_corrimao_faixa_m=f"{ALTURA_CORRIMAO_MINIMA_M} m a {ALTURA_CORRIMAO_MAXIMA_M} m",
        exige_corrimao_central=exige_corrimao_central,
    )

    # Diretrizes e recomendações normativas
    recomendacoes.append(
        f"Tipologia de escada adotada: '{dados.tipo_escada.value}' conforme ABNT NBR 9077:2001."
    )
    recomendacoes.append(
        "Portas de saída de emergência devem abrir no sentido do fluxo de escape e não diminuir a largura útil de corredores."
    )
    recomendacoes.append(
        "Lances de escada devem conter entre 3 e 16 degraus, com patamar intermediário a cada no máximo 3,20 m de desnível."
    )
    recomendacoes.append(
        f"Guarda-corpos devem ter altura mínima de {alt_gc} m e vão livre máximo entre barras verticais de {VAO_MAXIMO_BARRAS_VERTICAIS_M} m (proibidas barras horizontais)."
    )
    if exige_corrimao_central:
        recomendacoes.append(
            f"Escada com largura de {maior_largura_escada} m (> 2,20 m) exige a instalação de corrimão intermediário central."
        )

    return ResultadoDimensionamento(
        nome_edificacao=dados.nome_edificacao,
        altura_total_m=dados.altura_total_m,
        tipo_escada=dados.tipo_escada,
        populacao_total_edificacao=populacao_total,
        degraus=res_degraus,
        guarda_corpo=res_gc,
        pavimentos=tuple(res_pavimentos),
        alertas=tuple(alertas),
        recomendacoes=tuple(recomendacoes),
    )


# Alias de conveniência
dimensionar_edificacao = dimensionar_saidas_edificacao

