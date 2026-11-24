"""Reglas del chat del partido (Sprint 14): solo participantes, texto corto y con límite de ritmo."""

from datetime import datetime, timedelta

from app.domain.errors import ConflictError, DomainError

MAX_LENGTH = 500
MAX_PER_MINUTE = 10
OPEN_AFTER_KICKOFF = timedelta(hours=48)
PAGE_SIZE = 50


def clean_body(text: str) -> str:
    clean = " ".join(text.split())
    if not 1 <= len(clean) <= MAX_LENGTH:
        raise DomainError("INVALID_MESSAGE", f"El mensaje debe tener entre 1 y {MAX_LENGTH} caracteres.")
    return clean


def closed_reason(kickoff: datetime, now: datetime, cancelled: bool) -> ConflictError | None:
    """El motivo por el que ya no se puede escribir, o None si el chat sigue abierto."""
    if cancelled:
        return ConflictError("CONTRACT_CANCELLED", "Este partido fue cancelado; el chat es de solo lectura.")
    if now > kickoff + OPEN_AFTER_KICKOFF:
        return ConflictError("CHAT_CLOSED", "El chat se cerró 48 horas después del partido.")
    return None


def check_rate(sent_last_minute: int) -> None:
    if sent_last_minute >= MAX_PER_MINUTE:
        raise ConflictError("TOO_MANY_MESSAGES", "Enviaste muchos mensajes seguidos. Espera un minuto.")
