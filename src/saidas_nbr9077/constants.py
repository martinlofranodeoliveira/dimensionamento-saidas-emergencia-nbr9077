"""Constantes e parâmetros normativos da ABNT NBR 9077:2001.

ABNT NBR 9077:2001 - Saídas de emergência em edifícios.
Fixa as condições exigíveis que as edificações devem satisfazer a fim de que sua
população possa abandoná-las em segurança em caso de incêndio ou pânico.
"""

from fractions import Fraction
from typing import Final

# Largura nominal da Unidade de Passagem (UP) em metros
LARGURA_UNIDADE_PASSAGEM_M: Final[Fraction] = Fraction(55, 100)  # 0.55 m

# Capacidades da Unidade de Passagem 'C' (número de pessoas por UP)
CAPACIDADE_UP_PORTAS_ACESSOS: Final[int] = 100         # 100 pessoas / UP (horizontal)
CAPACIDADE_UP_ESCADAS_GERAL: Final[int] = 60          # 60 pessoas / UP (escadas/rampas geral)
CAPACIDADE_UP_ESCADAS_REUNIAO_F: Final[int] = 45      # 45 pessoas / UP (locais de reunião F)

# Larguras mínimas regulamentares de saídas (metros)
LARGURA_MINIMA_SAIDA_GERAL_M: Final[Fraction] = Fraction(12, 10)        # 1.20 m (2 UP padrão)
LARGURA_MINIMA_PORTA_SECUNDARIA_M: Final[Fraction] = Fraction(8, 10)    # 0.80 m
LARGURA_MINIMA_HOSPITAIS_LEITOS_M: Final[Fraction] = Fraction(22, 10)   # 2.20 m
LARGURA_MINIMA_REUNIAO_GRANDE_M: Final[Fraction] = Fraction(22, 10)     # 2.20 m

# Parâmetros ergonômicos de degraus de escada (Fórmula de Blondel)
BLONDEL_MINIMO_M: Final[Fraction] = Fraction(63, 100)  # 0.63 m (63 cm)
BLONDEL_MAXIMO_M: Final[Fraction] = Fraction(64, 100)  # 0.64 m (64 cm)

ALTURA_ESPELHO_MINIMA_M: Final[Fraction] = Fraction(16, 100)   # 0.16 m (16.0 cm)
ALTURA_ESPELHO_MAXIMA_M: Final[Fraction] = Fraction(18, 100)   # 0.18 m (18.0 cm)
LARGURA_PISO_MINIMA_M: Final[Fraction] = Fraction(27, 100)     # 0.27 m (27.0 cm)

# Quantidade de degraus e desnível por lance de escada
DEGRAUS_MINIMOS_POR_LANCE: Final[int] = 3
DEGRAUS_MAXIMOS_POR_LANCE: Final[int] = 16
DESNIVEL_MAXIMO_PATAMAR_M: Final[Fraction] = Fraction(32, 10)  # 3.20 m

# Guarda-corpos e corrimãos
ALTURA_MINIMA_GUARDA_CORPO_BAIXA_M: Final[Fraction] = Fraction(105, 100)  # 1.05 m (desnível <= 12m)
ALTURA_MINIMA_GUARDA_CORPO_ALTA_M: Final[Fraction] = Fraction(130, 100)   # 1.30 m (desnível > 12m)
VAO_MAXIMO_BARRAS_VERTICAIS_M: Final[Fraction] = Fraction(11, 100)        # 0.11 m (11.0 cm)

ALTURA_CORRIMAO_MINIMA_M: Final[Fraction] = Fraction(80, 100)   # 0.80 m
ALTURA_CORRIMAO_MAXIMA_M: Final[Fraction] = Fraction(92, 100)   # 0.92 m
LARGURA_LIMITE_CORRIMAO_CENTRAL_M: Final[Fraction] = Fraction(22, 10)  # > 2.20 m exige corrimão central

# Distâncias máximas a percorrer até a saída protegida (metros) - Tabela 2 NBR 9077
DISTANCIA_MAX_UNICA_SEM_SPRINKLERS_M: Final[Fraction] = Fraction(30, 1)  # 30 m
DISTANCIA_MAX_MULTIPLA_SEM_SPRINKLERS_M: Final[Fraction] = Fraction(45, 1)  # 45 m

# Com chuveiros automáticos (sprinklers) há majoração normativa de 50%
DISTANCIA_MAX_UNICA_COM_SPRINKLERS_M: Final[Fraction] = Fraction(45, 1)     # 45 m
DISTANCIA_MAX_MULTIPLA_COM_SPRINKLERS_M: Final[Fraction] = Fraction(65, 1)  # 65 m
