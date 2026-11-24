"""Reglas de solicitudes de partido y ofertas (Sprint 2).

Las fechas se comparan con zona horaria. El árbitro es opcional (decisión del dueño, 23/11/2026)
y el lugar puede ser un establecimiento, un lugar informal (parque) o quedar por acordar.
"""

from datetime import datetime, timedelta
from enum import StrEnum

from app.domain.errors import DomainError

MAX_WINDOW = timedelta(days=14)
MAX_AHEAD = timedelta(days=60)
MAX_OPEN_REQUESTS_PER_TEAM = 3


class RefereeMode(StrEnum):
    WITH = "WITH"
    WITHOUT = "WITHOUT"
    EITHER = "EITHER"


class PlaceKind(StrEnum):
    VENUE = "VENUE"
    INFORMAL = "INFORMAL"
    TO_AGREE = "TO_AGREE"


class RequestStatus(StrEnum):
    OPEN = "OPEN"
    MATCHED = "MATCHED"
    CANCELLED = "CANCELLED"


class OfferStatus(StrEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"
    SUPERSEDED = "SUPERSEDED"
    CANCELLED = "CANCELLED"


def validate_window(start: datetime, end: datetime, now: datetime) -> None:
    if start < now:
        raise DomainError("WINDOW_IN_PAST", "La fecha de inicio ya pasó. Elige una fecha futura.")
    if end <= start:
        raise DomainError("WINDOW_INVERTED", "La fecha final debe ser posterior a la inicial.")
    if end - start > MAX_WINDOW:
        raise DomainError("WINDOW_TOO_LONG", "La ventana para jugar puede durar máximo 14 días.")
    if start - now > MAX_AHEAD:
        raise DomainError("WINDOW_TOO_FAR", "Solo se pueden buscar partidos en los próximos 60 días.")


def check_proposed_start(proposed: datetime, start: datetime, end: datetime, now: datetime) -> None:
    if proposed < now:
        raise DomainError("OFFER_IN_PAST", "La hora propuesta ya pasó. Propón una hora futura.")
    if not start <= proposed <= end:
        raise DomainError("OFFER_OUTSIDE_WINDOW", "La hora propuesta debe estar dentro de la ventana del rival.")


def check_offer_referee(requested: RefereeMode, offered: RefereeMode) -> None:
    if offered == RefereeMode.EITHER:
        raise DomainError("REFEREE_MODE_REQUIRED", "En la oferta indica si el partido es con o sin árbitro.")
    if requested != RefereeMode.EITHER and requested != offered:
        raise DomainError(
            "REFEREE_MODE_MISMATCH",
            "El rival pidió un partido " + ("con árbitro." if requested == RefereeMode.WITH else "sin árbitro."),
        )
