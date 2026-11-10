"""Pacote para dimensionamento de saídas de emergência em edifícios (ABNT NBR 9077:2001).

Desenvolvido segundo as diretrizes de engenharia de software da Lofrano Tecnologia:
- 100% em português brasileiro (pt-BR);
- Zero dependências externas em tempo de execução;
- Aritmética racional exata (fractions.Fraction) sem IEEE float;
- Codecs JSON RFC 8259 estritos e relatórios com proteção contra injeção CSV.
"""

from saidas_nbr9077.calculator import (
    dimensionar_pavimento,
    dimensionar_saidas_edificacao,
    dimensionar_edificacao,
    obter_fator_area_por_pessoa,
    verificar_degraus_blondel,
)
from saidas_nbr9077.codecs import (
    carregar_dados_saidas_json,
    exportar_resultado_json,
)
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
    LARGURA_MINIMA_SAIDA_GERAL_M,
    LARGURA_PISO_MINIMA_M,
    LARGURA_UNIDADE_PASSAGEM_M,
)
from saidas_nbr9077.exporters import (
    gerar_csv_sanitizado,
    gerar_pacote_zip,
    gerar_relatorio_texto,
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
    TipoEscada,
)
from saidas_nbr9077.svg_generator import gerar_painel_svg

__version__ = "1.0.0"

__all__ = [
    "__version__",
    "dimensionar_saidas_edificacao",
    "dimensionar_edificacao",
    "dimensionar_pavimento",
    "obter_fator_area_por_pessoa",
    "verificar_degraus_blondel",
    "carregar_dados_saidas_json",
    "exportar_resultado_json",
    "gerar_relatorio_texto",
    "gerar_csv_sanitizado",
    "gerar_pacote_zip",
    "gerar_painel_svg",
    "DadosDegrau",
    "DadosPavimento",
    "DadosEdificacao",
    "GrupoOcupacao",
    "TipoEscada",
    "ResultadoDegraus",
    "ResultadoGuardaCorpo",
    "ResultadoPavimento",
    "ResultadoDimensionamento",
    "LARGURA_UNIDADE_PASSAGEM_M",
    "CAPACIDADE_UP_PORTAS_ACESSOS",
    "CAPACIDADE_UP_ESCADAS_GERAL",
    "CAPACIDADE_UP_ESCADAS_REUNIAO_F",
    "LARGURA_MINIMA_SAIDA_GERAL_M",
    "BLONDEL_MINIMO_M",
    "BLONDEL_MAXIMO_M",
    "ALTURA_ESPELHO_MINIMA_M",
    "ALTURA_ESPELHO_MAXIMA_M",
    "LARGURA_PISO_MINIMA_M",
    "ALTURA_MINIMA_GUARDA_CORPO_BAIXA_M",
    "ALTURA_MINIMA_GUARDA_CORPO_ALTA_M",
    "ALTURA_CORRIMAO_MINIMA_M",
    "ALTURA_CORRIMAO_MAXIMA_M",
    "DISTANCIA_MAX_UNICA_SEM_SPRINKLERS_M",
    "DISTANCIA_MAX_MULTIPLA_SEM_SPRINKLERS_M",
    "DISTANCIA_MAX_UNICA_COM_SPRINKLERS_M",
    "DISTANCIA_MAX_MULTIPLA_COM_SPRINKLERS_M",
]
