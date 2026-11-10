"""Modelos de dados e estruturas imutáveis para saídas de emergência NBR 9077:2001."""

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Optional


class GrupoOcupacao(str, Enum):
    """Classificação das ocupações conforme Tabela 1 da ABNT NBR 9077."""
    A_RESIDENCIAL = "A"                   # Habitação unifamiliar e multifamiliar
    B_HOSPEDAGEM = "B"                    # Hotéis, motéis, pensões
    C_COMERCIAL = "C"                     # Comércio varejista e atacadista
    D_SERVICOS_PROFISSIONAIS = "D"        # Escritórios, consultórios, bancos
    E_EDUCACIONAL = "E"                   # Escolas, creches, universidades
    F_REUNIAO_PUBLICO = "F"               # Teatros, cinemas, clubes, estádios
    G_GARAGEM = "G"                       # Garagens e postos de serviço
    H_SERVICOS_SAUDE = "H"                # Hospitais, clínicas, prontos-socorros
    I_INDUSTRIAL = "I"                    # Indústrias e fábricas
    J_DEPOSITO = "J"                      # Depósitos e armazéns


class TipoEscada(str, Enum):
    """Tipologia de escada de segurança segundo enclausuramento e proteção."""
    NAO_ENCLAUSURADA = "nao_enclausurada"                     # Escada comum (NE)
    ENCLAUSURADA_PROTEGIDA = "enclausurada_protegida"         # Escada protegida com PCF (EP)
    ENCLAUSURADA_FUMACA = "enclausurada_a_prova_de_fumaca"    # Com antecâmara/duto (PF)
    PRESSURIZADA = "pressurizada"                             # Mecanicamente pressurizada (P)


@dataclass(frozen=True)
class DadosDegrau:
    """Parâmetros geométricos de piso e espelho do degrau da escada."""
    altura_espelho_m: Fraction
    largura_piso_m: Fraction

    def __post_init__(self) -> None:
        if self.altura_espelho_m <= Fraction(0, 1):
            raise ValueError(f"Altura do espelho ({self.altura_espelho_m}m) deve ser estritamente positiva.")
        if self.largura_piso_m <= Fraction(0, 1):
            raise ValueError(f"Largura do piso ({self.largura_piso_m}m) deve ser estritamente positiva.")


@dataclass(frozen=True)
class DadosPavimento:
    """Dados arquitetônicos e populacionais de um pavimento a dimensionar."""
    nome_pavimento: str
    grupo_ocupacao: GrupoOcupacao
    area_liquida_m2: Fraction
    distancia_percorrer_m: Fraction
    quantidade_saidas_instaladas: int
    populacao_fixada: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.nome_pavimento or not self.nome_pavimento.strip():
            raise ValueError("O nome do pavimento não pode ser vazio.")
        if self.area_liquida_m2 <= Fraction(0, 1):
            raise ValueError(f"Área líquida ({self.area_liquida_m2}m²) deve ser estritamente positiva.")
        if self.distancia_percorrer_m <= Fraction(0, 1):
            raise ValueError(f"Distância a percorrer ({self.distancia_percorrer_m}m) deve ser positiva.")
        if self.quantidade_saidas_instaladas <= 0:
            raise ValueError("A quantidade de saídas instaladas deve ser de no mínimo 1.")
        if self.populacao_fixada is not None and self.populacao_fixada <= 0:
            raise ValueError(f"População fixada ({self.populacao_fixada}) deve ser estritamente positiva.")


@dataclass(frozen=True)
class DadosEdificacao:
    """Conjunto de parâmetros da edificação para dimensionamento NBR 9077."""
    nome_edificacao: str
    altura_total_m: Fraction
    tipo_escada: TipoEscada
    possui_sprinklers: bool
    dados_degrau: DadosDegrau
    pavimentos: tuple[DadosPavimento, ...]

    def __post_init__(self) -> None:
        if not self.nome_edificacao or not self.nome_edificacao.strip():
            raise ValueError("O nome da edificação não pode ser vazio.")
        if self.altura_total_m <= Fraction(0, 1):
            raise ValueError(f"Altura total ({self.altura_total_m}m) deve ser estritamente positiva.")
        if not self.pavimentos:
            raise ValueError("A edificação deve conter ao menos um pavimento cadastrado.")


@dataclass(frozen=True)
class ResultadoDegraus:
    """Verificação ergonômica de degraus de escada segundo Blondel."""
    altura_espelho_m: Fraction
    largura_piso_m: Fraction
    valor_blondel_m: Fraction
    conforme_blondel: bool
    conforme_espelho: bool
    conforme_piso: bool
    conforme_geral: bool
    patamar_minimo_m: Fraction


@dataclass(frozen=True)
class ResultadoGuardaCorpo:
    """Dimensionamento e alturas normativas de guarda-corpos e corrimãos."""
    altura_minima_guarda_corpo_m: Fraction
    vao_maximo_barras_m: Fraction
    altura_corrimao_faixa_m: str
    exige_corrimao_central: bool


@dataclass(frozen=True)
class ResultadoPavimento:
    """Resultados de dimensionamento de saídas de emergência por pavimento."""
    nome_pavimento: str
    grupo_ocupacao: GrupoOcupacao
    area_liquida_m2: Fraction
    populacao_calculada: int
    unidades_passagem_portas: int
    largura_minima_portas_m: Fraction
    unidades_passagem_escadas: int
    largura_minima_escadas_m: Fraction
    distancia_percorrer_m: Fraction
    distancia_maxima_permitida_m: Fraction
    conforme_distancia: bool
    saidas_minimas_exigidas: int
    saidas_instaladas: int
    conforme_saidas: bool


@dataclass(frozen=True)
class ResultadoDimensionamento:
    """Resultado técnico completo consolidado da ABNT NBR 9077:2001."""
    nome_edificacao: str
    altura_total_m: Fraction
    tipo_escada: TipoEscada
    populacao_total_edificacao: int
    degraus: ResultadoDegraus
    guarda_corpo: ResultadoGuardaCorpo
    pavimentos: tuple[ResultadoPavimento, ...]
    alertas: tuple[str, ...]
    recomendacoes: tuple[str, ...]
