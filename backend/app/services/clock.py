"""Reloj inyectable: el sistema real usa UTC; las pruebas usan un reloj fijo."""

from datetime import UTC, date, datetime, timedelta, timezone
from typing import Protocol

# Colombia no usa horario de verano; un desfase fijo evita depender de tzdata en Windows.
COLOMBIA_TZ = timezone(timedelta(hours=-5), name="America/Bogota")


class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


class FixedClock:
    def __init__(self, start: datetime) -> None:
        self._now = start

    def now(self) -> datetime:
        return self._now

    def advance(self, delta: timedelta) -> None:
        self._now = self._now + delta


def local_today(clock: Clock) -> date:
    """Fecha calendario en Colombia, usada para calcular la edad."""
    return clock.now().astimezone(COLOMBIA_TZ).date()
