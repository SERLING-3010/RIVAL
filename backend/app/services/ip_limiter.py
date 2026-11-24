"""Límite por equipo cliente (IP) con ventana deslizante, para registro e inicio de sesión.

Complementa al límite por correo: impide probar muchos correos distintos desde el mismo
lugar (enumeración de cuentas y consumo de CPU por Argon2). En memoria y con purga
periódica; con varios procesos se moverá a Redis (ADR-003).

[POR VERIFICAR] Detrás de un proxy, la IP debe venir de un encabezado de confianza
configurable; hoy se usa la IP de la conexión.
"""

from collections import deque
from datetime import datetime, timedelta
from threading import Lock

from app.domain.errors import RateLimitedError

MAX_TRACKED_KEYS = 10_000


class SlidingWindowLimiter:
    def __init__(self, max_events: int, window: timedelta) -> None:
        self._max_events = max_events
        self._window = window
        self._events: dict[str, deque[datetime]] = {}
        self._lock = Lock()

    def hit(self, key: str, now: datetime) -> None:
        """Cuenta un intento; si ya se superó el máximo en la ventana, lo rechaza."""
        with self._lock:
            if len(self._events) > MAX_TRACKED_KEYS:
                self._purge(now)
            events = self._events.setdefault(key, deque())
            while events and now - events[0] >= self._window:
                events.popleft()
            if len(events) >= self._max_events:
                wait = int((events[0] + self._window - now).total_seconds()) + 1
                raise RateLimitedError(
                    "TOO_MANY_REQUESTS",
                    f"Demasiados intentos desde este equipo. Espera {wait} segundos.",
                    retry_after_seconds=wait,
                )
            events.append(now)

    def _purge(self, now: datetime) -> None:
        stale = [k for k, v in self._events.items() if not v or now - v[-1] >= self._window]
        for key in stale:
            del self._events[key]


def register_limiter() -> SlidingWindowLimiter:
    return SlidingWindowLimiter(max_events=10, window=timedelta(hours=1))


def login_ip_limiter() -> SlidingWindowLimiter:
    return SlidingWindowLimiter(max_events=30, window=timedelta(minutes=15))


def search_limiter() -> SlidingWindowLimiter:
    """Búsquedas de rivales, partidos y agentes libres por usuario."""
    return SlidingWindowLimiter(max_events=60, window=timedelta(minutes=10))
