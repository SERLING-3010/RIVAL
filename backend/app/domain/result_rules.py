"""Reglas del resultado del partido (Sprint 4, RIV-013).

Sin árbitro, el resultado vale cuando los dos administradores reportan el mismo marcador;
si no coinciden, el partido queda en disputa y no suma a estadísticas (Sprint 0, 4.4.1).
"""

from datetime import datetime
from enum import StrEnum

from app.domain.errors import DomainError

MAX_SCORE = 999


class ResultStatus(StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    DISPUTED = "DISPUTED"


def check_can_report(kickoff: datetime, now: datetime) -> None:
    if now < kickoff:
        raise DomainError("RESULT_TOO_EARLY", "El resultado se reporta cuando el partido ya empezó.")


def validate_score(host: int, guest: int) -> None:
    if not (0 <= host <= MAX_SCORE and 0 <= guest <= MAX_SCORE):
        raise DomainError("SCORE_OUT_OF_RANGE", "El marcador de cada equipo va de 0 a 999.")


def resolve_result(reports: list[tuple[int, int]]) -> tuple[ResultStatus, tuple[int, int] | None]:
    """Con dos reportes iguales hay resultado; distintos, disputa; menos de dos, pendiente."""
    if len(reports) < 2:
        return ResultStatus.PENDING, None
    first, second = reports[0], reports[1]
    if first == second:
        return ResultStatus.CONFIRMED, first
    return ResultStatus.DISPUTED, None
