"""Reglas de establecimientos, canchas, franjas y reservas (Sprint 6, RIV-012).

La tarifa es solo de referencia: el pago de la cancha se hace fuera de la app (decisión del dueño).
El dinero se maneja siempre como Decimal exacto.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum

from app.domain.errors import DomainError
from app.domain.match_rules import MAX_AHEAD

MIN_SLOT = timedelta(minutes=30)
MAX_SLOT = timedelta(minutes=240)
MAX_PRICE = Decimal("10000000")


class BookingStatus(StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


ACTIVE_BOOKINGS = (BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value)
Interval = tuple[datetime, datetime]


def validate_address(address: str) -> str:
    clean = " ".join(address.split())
    if not 5 <= len(clean) <= 120:
        raise DomainError("INVALID_ADDRESS", "La dirección debe tener entre 5 y 120 caracteres.")
    return clean


def validate_reference_price(price: Decimal | None) -> Decimal | None:
    if price is None:
        return None
    exponent = price.as_tuple().exponent
    if price < 0 or price > MAX_PRICE or (isinstance(exponent, int) and exponent < -2):
        raise DomainError("INVALID_REFERENCE_PRICE", "La tarifa de referencia va de 0 a 10.000.000 pesos.")
    return price.quantize(Decimal("0.01"))


def validate_slot(start: datetime, end: datetime, now: datetime) -> None:
    if start <= now:
        raise DomainError("SLOT_IN_PAST", "La franja debe empezar en el futuro.")
    if start - now > MAX_AHEAD:
        raise DomainError("SLOT_TOO_FAR", "Solo se publican franjas de los próximos 60 días.")
    if not MIN_SLOT <= end - start <= MAX_SLOT:
        raise DomainError("SLOT_DURATION_OUT_OF_RANGE", "Una franja dura entre 30 minutos y 4 horas.")


def slots_overlap(a: Interval, b: Interval) -> bool:
    """Intervalos semiabiertos: una franja que termina a las 8 no choca con una que empieza a las 8."""
    return a[0] < b[1] and b[0] < a[1]


def check_slot_covers_match(slot: Interval, kickoff: datetime, duration_minutes: int) -> None:
    if not (slot[0] <= kickoff and kickoff + timedelta(minutes=duration_minutes) <= slot[1]):
        raise DomainError("SLOT_DOES_NOT_COVER_MATCH", "La franja debe cubrir todo el partido: hora de inicio y duración.")
