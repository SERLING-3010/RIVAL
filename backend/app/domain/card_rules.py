"""Carta del jugador (Sprints 20 y 23): media de 0 a 99, carta básica y valor de mercado, solo con datos reales.

Fórmula de la media [SUPUESTO, ajustable con el piloto]: base 40, hasta 30 por la valoración de
compañeros (promedio de 1 a 10 por 3; con menos de 3 votos cuenta 5,5 neutral), hasta 15 por
experiencia (tope 50 partidos), hasta 10 por porcentaje de victorias y hasta 4 por goles por partido.

Carta básica (decisión del dueño, Sprint 23): sale solo de la media actual y sube o baja con ella.
Bronce hasta 64, Plata de 65 a 74, Oro común de 75 a 79 y Oro brillante desde 80. Las cartas
especiales, que piden además hazañas, están en `special_cards`. Nada de esto se compra.
"""

import math
from dataclasses import dataclass

BASE, MAX_MEDIA = 40, 99
MIN_VOTES, NEUTRAL_RATING = 3, 5.5

# (código, media desde la que se tiene)
BASE_TIERS: list[tuple[str, int]] = [("BRONCE", 0), ("PLATA", 65), ("ORO", 75), ("ORO_BRILLANTE", 80)]


@dataclass(frozen=True)
class Tier:
    name: str
    rank: int  # 1 = Bronce … 4 = Oro brillante
    next_name: str | None
    media_to_next: int  # 0 si ya es la última carta básica


def media(matches: int, wins: int, goals: int, rating_average: float | None, votes: int) -> int:
    rating = rating_average if rating_average is not None and votes >= MIN_VOTES else NEUTRAL_RATING
    experience = min(matches, 50) / 50 * 15
    effectiveness = (wins / matches) * 10 if matches else 0.0
    scoring = min(goals / matches, 1.0) * 4 if matches else 0.0
    total = BASE + rating * 3 + experience + effectiveness + scoring
    return min(MAX_MEDIA, math.floor(total + 0.5))  # ,5 hacia arriba (round() de Python iría al par)


def tier(card_media: int) -> Tier:
    """La carta básica de esa media."""
    current = max(i for i, (_, floor) in enumerate(BASE_TIERS) if card_media >= floor)
    if current == len(BASE_TIERS) - 1:
        return Tier(BASE_TIERS[current][0], current + 1, None, 0)
    next_name, floor = BASE_TIERS[current + 1]
    return Tier(BASE_TIERS[current][0], current + 1, next_name, floor - card_media)


def market_value(card_media: int, rank: int, specials: int, recent: list[str]) -> int:
    """Valor en monedas RIVAL virtuales [SUPUESTO]: media × 5, 25 por carta básica, 40 por especial y forma.

    Cada victoria de los últimos cinco partidos suma 10 y cada empate 4. Se redondea a decenas.
    Es una referencia para el mercado: no se compra, no se vende ni se cambia por dinero.
    """
    form = sum(10 if r == "W" else 4 if r == "D" else 0 for r in recent)
    raw = card_media * 5 + (rank - 1) * 25 + specials * 40 + form
    return int(math.floor(raw / 10 + 0.5) * 10)
