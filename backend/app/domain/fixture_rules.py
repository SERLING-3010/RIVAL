"""Calendario de la liga: todos contra todos por el método del círculo (Sprint 8).

Con número impar de equipos se agrega un "descanso": quien le toca, no juega esa fecha.
"""

from datetime import datetime, timedelta

from app.domain.errors import DomainError
from app.domain.match_rules import MAX_AHEAD

Pairing = tuple[int, int]  # (local, visitante)


def round_robin(team_ids: list[int]) -> list[list[Pairing]]:
    if len(team_ids) < 2:
        raise DomainError("FIXTURE_NEEDS_TEAMS", "Se necesitan al menos 2 equipos aprobados para el calendario.")
    slots: list[int | None] = list(team_ids) + ([None] if len(team_ids) % 2 else [])
    rounds: list[list[Pairing]] = []
    for number in range(len(slots) - 1):
        pairs: list[Pairing] = []
        for i in range(len(slots) // 2):
            a, b = slots[i], slots[-1 - i]
            if a is not None and b is not None:
                pairs.append((a, b) if (number + i) % 2 == 0 else (b, a))  # alterna quién es local
        rounds.append(pairs)
        slots = [slots[0], slots[-1], *slots[1:-1]]  # rota todos menos el primero
    return rounds


def round_dates(first: datetime, days_between: int, rounds: int, now: datetime) -> list[datetime]:
    if first <= now:
        raise DomainError("FIXTURE_IN_PAST", "La primera fecha debe ser en el futuro.")
    if not 1 <= days_between <= 14:
        raise DomainError("FIXTURE_GAP_OUT_OF_RANGE", "Entre fechas deben pasar de 1 a 14 días.")
    dates = [first + timedelta(days=days_between * n) for n in range(rounds)]
    if dates[-1] - now > MAX_AHEAD:
        raise DomainError("FIXTURE_TOO_LONG",
                          "La última fecha debe caer en los próximos 60 días. Acorta los días entre fechas.")
    return dates
