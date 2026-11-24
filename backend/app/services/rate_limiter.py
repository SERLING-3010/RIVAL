"""Límite de intentos de inicio de sesión con espera creciente.

Tras MAX_FAILURES fallos seguidos para la misma clave (correo + equipo cliente), el inicio
de sesión se bloquea BASE_LOCK_SECONDS y la espera se duplica en cada fallo adicional,
hasta MAX_LOCK_SECONDS. En memoria: suficiente para un solo proceso (Sprint 1);
con varios procesos se moverá a Redis (ADR-003).
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import Lock

from app.domain.errors import RateLimitedError

MAX_FAILURES = 5
BASE_LOCK_SECONDS = 30
MAX_LOCK_SECONDS = 15 * 60
MAX_TRACKED_KEYS = 10_000


@dataclass
class _Entry:
    failures: int = 0
    locked_until: datetime | None = None
    last_failure_at: datetime | None = None


class LoginRateLimiter:
    def __init__(self) -> None:
        self._entries: dict[str, _Entry] = {}
        self._lock = Lock()

    def check(self, key: str, now: datetime) -> None:
        with self._lock:
            entry = self._entries.get(key)
            if entry and entry.locked_until and entry.locked_until > now:
                wait = int((entry.locked_until - now).total_seconds()) + 1
                raise RateLimitedError(
                    "TOO_MANY_ATTEMPTS",
                    f"Demasiados intentos. Espera {wait} segundos e inténtalo de nuevo.",
                    retry_after_seconds=wait,
                )

    def register_failure(self, key: str, now: datetime) -> None:
        with self._lock:
            if len(self._entries) > MAX_TRACKED_KEYS:
                self._purge(now)
            entry = self._entries.setdefault(key, _Entry())
            entry.failures += 1
            entry.last_failure_at = now
            if entry.failures >= MAX_FAILURES:
                extra = entry.failures - MAX_FAILURES
                seconds = min(BASE_LOCK_SECONDS * (2**extra), MAX_LOCK_SECONDS)
                entry.locked_until = now + timedelta(seconds=seconds)

    def _purge(self, now: datetime) -> None:
        """Olvida claves sin bloqueo vigente y sin fallos recientes, para que la memoria no crezca sin tope."""
        horizon = timedelta(seconds=MAX_LOCK_SECONDS)
        stale = [
            k for k, e in self._entries.items()
            if (e.locked_until is None or e.locked_until <= now)
            and (e.last_failure_at is None or now - e.last_failure_at > horizon)
        ]
        for key in stale:
            del self._entries[key]

    def tracked_keys(self) -> int:
        return len(self._entries)

    def register_success(self, key: str) -> None:
        with self._lock:
            self._entries.pop(key, None)
