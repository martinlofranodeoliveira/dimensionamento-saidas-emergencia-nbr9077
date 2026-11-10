"""Codec JSON canônico RFC 8259 para saídas de emergência NBR 9077:2001."""

import json
from enum import Enum
from fractions import Fraction
from typing import Any

from saidas_nbr9077.models import (
    DadosDegrau,
    DadosEdificacao,
    DadosPavimento,
    GrupoOcupacao,
    ResultadoDimensionamento,
    TipoEscada,
)


def _rejeitar_float(valor: str) -> None:
    raise ValueError(f"Ponto flutuante ({valor}) não é permitido. Utilize inteiros ou strings decimais exatas.")


def _rejeitar_chaves_duplicadas(pares: list[tuple[str, Any]]) -> dict[str, Any]:
    resultado: dict[str, Any] = {}
    for chave, valor in pares:
        if chave in resultado:
            raise ValueError(f"Chave duplicada encontrada no JSON: '{chave}'")
        resultado[chave] = valor
    return resultado


def _verificar_profundidade(obj: Any, profundidade: int = 1, limite: int = 32) -> None:
    if profundidade > limite:
        raise ValueError(f"Profundidade da estrutura JSON ({profundidade}) excede o limite máximo permitido de {limite}.")
    if isinstance(obj, dict):
        for v in obj.values():
            _verificar_profundidade(v, profundidade + 1, limite)
    elif isinstance(obj, list):
        for elem in obj:
            _verificar_profundidade(elem, profundidade + 1, limite)


def _para_fracao(val: Any) -> Fraction:
    if isinstance(val, (int, str)):
        return Fraction(val)
    if isinstance(val, Fraction):
        return val
    raise ValueError(f"Tipo inválido para conversão fracionária: {type(val).__name__} ({val})")


def carregar_dados_saidas_json(conteudo: str) -> DadosEdificacao:
    """Carrega e valida os dados de saídas de emergência em JSON canônico sem float."""
    if conteudo.startswith(("\ufeff", "\xef\xbb\xbf")):
        raise ValueError("Byte Order Mark (BOM) detectado. O arquivo deve ser codificado estritamente em UTF-8 puro.")

    try:
        dados = json.loads(
            conteudo,
            object_pairs_hook=_rejeitar_chaves_duplicadas,
            parse_float=_rejeitar_float,
        )
    except json.JSONDecodeError as err:
        raise ValueError(f"Erro de decodificação JSON: {err}") from err

    _verificar_profundidade(dados)

    if not isinstance(dados, dict):
        raise ValueError("O JSON raiz deve ser um objeto dicionário.")

    nome = str(dados.get("nome_edificacao", "Edifício"))
    altura = _para_fracao(dados.get("altura_total_m", "12.0"))

    tipo_escada_str = str(dados.get("tipo_escada", "enclausurada_protegida")).lower()
    try:
        tipo_escada = TipoEscada(tipo_escada_str)
    except ValueError:
        tipo_escada = TipoEscada.ENCLAUSURADA_PROTEGIDA

    possui_sprinklers = bool(dados.get("possui_sprinklers", False))

    degraus_raw = dados.get("dados_degrau", {})
    if not isinstance(degraus_raw, dict):
        raise ValueError("O campo 'dados_degrau' deve ser um dicionário.")
    h_espelho = _para_fracao(degraus_raw.get("altura_espelho_m", "0.175"))
    b_piso = _para_fracao(degraus_raw.get("largura_piso_m", "0.28"))
    degraus = DadosDegrau(altura_espelho_m=h_espelho, largura_piso_m=b_piso)

    lista_pavs_raw = dados.get("pavimentos", [])
    if not isinstance(lista_pavs_raw, list):
        raise ValueError("O campo 'pavimentos' deve ser uma lista.")

    pavimentos_parsed: list[DadosPavimento] = []
    for idx, p_dict in enumerate(lista_pavs_raw):
        if not isinstance(p_dict, dict):
            raise ValueError(f"Pavimento no índice {idx} deve ser um dicionário.")

        nome_p = str(p_dict.get("nome_pavimento", f"Pavimento {idx + 1}"))
        grupo_str = str(p_dict.get("grupo_ocupacao", "D")).upper()
        try:
            grupo = GrupoOcupacao(grupo_str)
        except ValueError:
            grupo = GrupoOcupacao.D_SERVICOS_PROFISSIONAIS

        area = _para_fracao(p_dict.get("area_liquida_m2", "300.0"))
        dist_p = _para_fracao(p_dict.get("distancia_percorrer_m", "25.0"))
        qtd_saidas = int(p_dict.get("quantidade_saidas_instaladas", 1))

        pop_fix = p_dict.get("populacao_fixada")
        pop_fixada_val = int(pop_fix) if pop_fix is not None else None

        pavimentos_parsed.append(
            DadosPavimento(
                nome_pavimento=nome_p,
                grupo_ocupacao=grupo,
                area_liquida_m2=area,
                distancia_percorrer_m=dist_p,
                quantidade_saidas_instaladas=qtd_saidas,
                populacao_fixada=pop_fixada_val,
            )
        )

    return DadosEdificacao(
        nome_edificacao=nome,
        altura_total_m=altura,
        tipo_escada=tipo_escada,
        possui_sprinklers=possui_sprinklers,
        dados_degrau=degraus,
        pavimentos=tuple(pavimentos_parsed),
    )


def _serializar_valor(val: Any) -> Any:
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return val.numerator
        return f"{val.numerator}/{val.denominator}"
    if isinstance(val, Enum):
        return val.value
    if isinstance(val, tuple):
        return [_serializar_valor(x) for x in val]
    if isinstance(val, dict):
        return {k: _serializar_valor(v) for k, v in val.items()}
    return val


def exportar_resultado_json(res: ResultadoDimensionamento) -> str:
    """Serializa o resultado em JSON canônico RFC 8259 determinístico."""
    dados: dict[str, Any] = {
        "norma": "ABNT NBR 9077:2001",
        "nome_edificacao": res.nome_edificacao,
        "altura_total_m": _serializar_valor(res.altura_total_m),
        "tipo_escada": res.tipo_escada.value,
        "populacao_total_edificacao": res.populacao_total_edificacao,
        "degraus": {
            "altura_espelho_m": _serializar_valor(res.degraus.altura_espelho_m),
            "largura_piso_m": _serializar_valor(res.degraus.largura_piso_m),
            "valor_blondel_m": _serializar_valor(res.degraus.valor_blondel_m),
            "conforme_blondel": res.degraus.conforme_blondel,
            "conforme_espelho": res.degraus.conforme_espelho,
            "conforme_piso": res.degraus.conforme_piso,
            "conforme_geral": res.degraus.conforme_geral,
            "patamar_minimo_m": _serializar_valor(res.degraus.patamar_minimo_m),
        },
        "guarda_corpo": {
            "altura_minima_guarda_corpo_m": _serializar_valor(res.guarda_corpo.altura_minima_guarda_corpo_m),
            "vao_maximo_barras_m": _serializar_valor(res.guarda_corpo.vao_maximo_barras_m),
            "altura_corrimao_faixa_m": res.guarda_corpo.altura_corrimao_faixa_m,
            "exige_corrimao_central": res.guarda_corpo.exige_corrimao_central,
        },
        "pavimentos": [
            {
                "nome_pavimento": p.nome_pavimento,
                "grupo_ocupacao": p.grupo_ocupacao.value,
                "area_liquida_m2": _serializar_valor(p.area_liquida_m2),
                "populacao_calculada": p.populacao_calculada,
                "unidades_passagem_portas": p.unidades_passagem_portas,
                "largura_minima_portas_m": _serializar_valor(p.largura_minima_portas_m),
                "unidades_passagem_escadas": p.unidades_passagem_escadas,
                "largura_minima_escadas_m": _serializar_valor(p.largura_minima_escadas_m),
                "distancia_percorrer_m": _serializar_valor(p.distancia_percorrer_m),
                "distancia_maxima_permitida_m": _serializar_valor(p.distancia_maxima_permitida_m),
                "conforme_distancia": p.conforme_distancia,
                "saidas_minimas_exigidas": p.saidas_minimas_exigidas,
                "saidas_instaladas": p.saidas_instaladas,
                "conforme_saidas": p.conforme_saidas,
            }
            for p in res.pavimentos
        ],
        "alertas": list(res.alertas),
        "recomendacoes": list(res.recomendacoes),
    }

    return json.dumps(dados, ensure_ascii=False, indent=2, sort_keys=True)
