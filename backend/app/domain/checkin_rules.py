"""Check-in en la cancha (Sprint 15): guarda solo "llegó" y la hora, nunca la posición de la persona."""

from datetime import datetime, timedelta

from app.domain.errors import ConflictError, DomainError

ARRIVAL_RADIUS_KM = 0.25  # [SUPUESTO] margen para el error del GPS de un teléfono
OPENS_BEFORE_KICKOFF = timedelta(minutes=60)


def closes_at(kickoff: datetime, duration_minutes: int) -> datetime:
    return kickoff + timedelta(minutes=duration_minutes)


def window_open(kickoff: datetime, duration_minutes: int, now: datetime) -> bool:
    return kickoff - OPENS_BEFORE_KICKOFF <= now <= closes_at(kickoff, duration_minutes)


def check_window(kickoff: datetime, duration_minutes: int, now: datetime) -> None:
    if now < kickoff - OPENS_BEFORE_KICKOFF:
        raise ConflictError("CHECKIN_NOT_OPEN", "El check-in abre 60 minutos antes del partido.")
    if not window_open(kickoff, duration_minutes, now):
        raise ConflictError("CHECKIN_CLOSED", "El partido ya terminó; el check-in está cerrado.")


def check_arrived(distance_km: float) -> None:
    if distance_km > ARRIVAL_RADIUS_KM:
        raise DomainError("NOT_AT_VENUE", "Todavía no estás en la cancha. Inténtalo cuando llegues.")
