"""Reglas del día del partido (Sprint 10): convocatoria y valoraciones entre compañeros."""

from datetime import datetime, timedelta
from enum import StrEnum

from app.domain.errors import ConflictError, DomainError

RATING_WINDOW = timedelta(days=7)


class CallUpStatus(StrEnum):
    INVITED = "INVITED"
    GOING = "GOING"
    NOT_GOING = "NOT_GOING"


def check_before_kickoff(kickoff: datetime, now: datetime) -> None:
    if now >= kickoff:
        raise ConflictError("MATCH_ALREADY_STARTED", "El partido ya empezó; la convocatoria está cerrada.")


def validate_score(score: int) -> None:
    if not 1 <= score <= 10:
        raise DomainError("INVALID_PLAYER_SCORE", "La valoración va de 1 a 10.")


def check_can_rate(rater_id: int, rated_id: int, played: set[int], kickoff: datetime, now: datetime) -> None:
    if rater_id == rated_id:
        raise DomainError("CANNOT_RATE_SELF", "No puedes valorarte a ti mismo.")
    if rated_id not in played:
        raise DomainError("PLAYER_NOT_IN_LINEUP", "Solo se valora a quien jugó el partido (planilla).")
    if now > kickoff + RATING_WINDOW:
        raise ConflictError("RATING_WINDOW_CLOSED", "Las valoraciones se hacen hasta 7 días después del partido.")
