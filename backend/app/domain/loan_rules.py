"""Préstamos por un partido y ventanas de traspasos (Sprint 13, Sprint 0 sección 4.2.2).

El jugador prestado no cambia de equipo: solo puede jugar ese partido con el otro equipo.
"""

from datetime import datetime
from enum import StrEnum

from app.domain.errors import ConflictError, DomainError


class LoanStatus(StrEnum):
    PENDING_OWNER = "PENDING_OWNER"
    PENDING_PLAYER = "PENDING_PLAYER"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


OPEN_LOANS = (LoanStatus.PENDING_OWNER.value, LoanStatus.PENDING_PLAYER.value, LoanStatus.ACTIVE.value)


def validate_window(starts_at: datetime, ends_at: datetime) -> None:
    if ends_at <= starts_at:
        raise DomainError("WINDOW_INVERTED", "La ventana de traspasos debe terminar después de empezar.")


def window_open(starts_at: datetime | None, ends_at: datetime | None, now: datetime) -> bool:
    """Sin ventana configurada, los traspasos están abiertos [SUPUESTO]."""
    if starts_at is None or ends_at is None:
        return True
    return starts_at <= now < ends_at


def check_window(open_now: bool) -> None:
    if not open_now:
        raise ConflictError("TRANSFER_WINDOW_CLOSED",
                            "La ventana de traspasos de la liga está cerrada. Espera a que se abra.")
