"""Rivales sugeridos con sus motivos (Sprint 18, P2 del Sprint 0: "sugerencias explicables").

Son reglas a la vista, no un modelo opaco: cada sugerencia dice por qué aparece. La cercanía se
dice por rangos (ADR-004), nunca en kilómetros exactos. Una sugerencia nunca sanciona ni bloquea.
"""

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.domain.geo import DistanceBand

LOCAL_OFFSET = timedelta(hours=-5)  # [SUPUESTO] el piloto es en Colombia (UTC-5, sin horario de verano)
CLOSE_LEVEL, NEAR_LEVEL = 100.0, 200.0
MAX_SUGGESTIONS = 5
DAY_NAMES = ["los lunes", "los martes", "los miércoles", "los jueves", "los viernes", "los sábados", "los domingos"]
_BAND_TEXT = {
    DistanceBand.UNDER_2_KM: (3, "Está a menos de 2 km"),
    DistanceBand.FROM_2_TO_5_KM: (2, "Está a entre 2 y 5 km"),
}


@dataclass(frozen=True)
class Signals:
    distance_band: DistanceBand | None
    my_level: float | None
    their_level: float | None
    my_days: list[datetime]  # horas de partido recientes de cada equipo
    their_days: list[datetime]
    played_recently: bool  # se enfrentaron en los últimos 30 días o ya tienen partido pactado


def favorite_day(kickoffs: list[datetime]) -> int | None:
    """Día de la semana (0 = lunes) en que más juega, en hora local; None sin partidos."""
    if not kickoffs:
        return None
    counts = Counter((k + LOCAL_OFFSET).weekday() for k in kickoffs)
    return max(sorted(counts), key=lambda d: counts[d])


def score(s: Signals) -> tuple[int, list[str]]:
    if s.played_recently:  # ya se enfrentaron o ya tienen partido pactado: no se sugiere
        return 0, []
    points, reasons = 0, []
    if s.distance_band in _BAND_TEXT:
        add, text = _BAND_TEXT[s.distance_band]
        points, reasons = points + add, reasons + [text]
    if s.my_level is not None and s.their_level is not None:
        gap = abs(s.my_level - s.their_level)
        if gap <= CLOSE_LEVEL:
            points, reasons = points + 3, reasons + ["Su nivel es parecido al tuyo"]
        elif gap <= NEAR_LEVEL:
            points, reasons = points + 1, reasons + ["Su nivel es cercano al tuyo"]
    mine, theirs = favorite_day(s.my_days), favorite_day(s.their_days)
    if mine is not None and mine == theirs:
        points, reasons = points + 2, reasons + [f"También juega {DAY_NAMES[mine]}"]
    return points + 1, reasons + ["No se han enfrentado en el último mes"]


def worth_suggesting(points: int, reasons: list[str]) -> bool:
    """Al menos un motivo fuerte (cercanía, nivel o día), no solo "no se han enfrentado"."""
    return points >= 3 and len(reasons) >= 2
