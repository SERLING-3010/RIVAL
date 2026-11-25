"""Carta del jugador (Sprint 20): media de 0 a 99 y nivel, solo con datos reales y sin compras.

Fórmula [SUPUESTO, ajustable con el piloto]: base 40, hasta 30 por la valoración de compañeros
(promedio de 1 a 10 por 3; con menos de 3 votos cuenta 5,5 neutral), hasta 15 por experiencia (tope
50 partidos), hasta 10 por porcentaje de victorias y hasta 4 por goles por partido (tope 1).
Nivel por partidos confirmados: Bronce 0-9, Plata 10-19, Oro 20-29, Élite 30 o más.
"""

import math
from dataclasses import dataclass

BASE, MAX_MEDIA = 40, 99
MIN_VOTES, NEUTRAL_RATING = 3, 5.5
TIERS = [("BRONCE", 0), ("PLATA", 10), ("ORO", 20), ("ELITE", 30)]


@dataclass(frozen=True)
class Tier:
    name: str
    next_name: str | None
    matches_to_next: int  # 0 si ya es el último nivel


def media(matches: int, wins: int, goals: int, rating_average: float | None, votes: int) -> int:
    rating = rating_average if rating_average is not None and votes >= MIN_VOTES else NEUTRAL_RATING
    experience = min(matches, 50) / 50 * 15
    effectiveness = (wins / matches) * 10 if matches else 0.0
    scoring = min(goals / matches, 1.0) * 4 if matches else 0.0
    total = BASE + rating * 3 + experience + effectiveness + scoring
    return min(MAX_MEDIA, math.floor(total + 0.5))  # ,5 hacia arriba (round() de Python iría al par)


def tier(matches: int) -> Tier:
    current = 0
    for i, (_, threshold) in enumerate(TIERS):
        if matches >= threshold:
            current = i
    if current == len(TIERS) - 1:
        return Tier(TIERS[current][0], None, 0)
    next_name, next_threshold = TIERS[current + 1]
    return Tier(TIERS[current][0], next_name, next_threshold - matches)
