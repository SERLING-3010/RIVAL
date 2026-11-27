"""Reglas de moderación (Sprint 12, Sprint 0 sección 4.8).

Las sanciones las aplica una persona, con motivo, y se pueden apelar ante otra (cuatro ojos).
Nunca hay sanciones automáticas.
"""

from datetime import datetime, timedelta
from enum import StrEnum

from app.domain.errors import ConflictError, DomainError, PermissionDeniedError

MAX_REPORTS_PER_DAY = 5
APPEAL_WINDOW = timedelta(days=14)


class ReportCategory(StrEnum):
    AGGRESSION = "AGGRESSION"
    NO_SHOW = "NO_SHOW"
    FAKE_PROFILE = "FAKE_PROFILE"
    OTHER = "OTHER"


class SanctionKind(StrEnum):
    WARNING = "WARNING"
    SUSPENSION = "SUSPENSION"


def validate_text(text: str, low: int, high: int, what: str) -> str:
    clean = " ".join(text.split())
    if not low <= len(clean) <= high:
        raise DomainError("INVALID_TEXT", f"{what} debe tener entre {low} y {high} caracteres.")
    return clean


def check_report_quota(reports_last_day: int) -> None:
    if reports_last_day >= MAX_REPORTS_PER_DAY:
        raise ConflictError("TOO_MANY_REPORTS", "Ya enviaste 5 reportes en las últimas 24 horas. Intenta mañana.")


def suspension_end(kind: SanctionKind, days: int | None, now: datetime) -> datetime | None:
    if kind == SanctionKind.WARNING:
        return None
    if days is None or not 1 <= days <= 30:
        raise DomainError("INVALID_SUSPENSION_DAYS", "La suspensión va de 1 a 30 días.")
    return now + timedelta(days=days)


def check_appeal_window(sanctioned_at: datetime, now: datetime) -> None:
    if now > sanctioned_at + APPEAL_WINDOW:
        raise ConflictError("APPEAL_WINDOW_CLOSED", "Las apelaciones se presentan dentro de 14 días.")


def check_four_eyes(sanctioned_by: int, appeal_decider: int) -> None:
    if sanctioned_by == appeal_decider:
        raise PermissionDeniedError("FOUR_EYES_REQUIRED", "La apelación la decide un moderador distinto del que sancionó.")
