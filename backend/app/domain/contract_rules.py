"""Reglas del contrato de partido (Sprint 3, RIV-009).

Las condiciones son un valor inmutable: un cambio crea una versión nueva. Sin dinero en la app
(decisión del dueño): el reparto de costos es solo un acuerdo escrito, sin montos.
"""

from dataclasses import asdict, dataclass, fields
from datetime import datetime
from enum import StrEnum
from typing import Any

from app.domain.errors import DomainError
from app.domain.match_rules import MAX_AHEAD, PlaceKind, RefereeMode


class ContractStatus(StrEnum):
    NEGOTIATING = "NEGOTIATING"
    SIGNED = "SIGNED"
    CANCELLED = "CANCELLED"


class CostSplit(StrEnum):
    HALF = "HALF"
    HOST = "HOST"
    GUEST = "GUEST"


@dataclass(frozen=True)
class ContractTerms:
    kickoff_at: datetime
    duration_minutes: int
    referee_mode: RefereeMode
    place_kind: PlaceKind
    place_note: str | None
    host_kit_color: str
    guest_kit_color: str
    substitutions: int | None  # None = ilimitados
    field_cost_split: CostSplit
    referee_cost_split: CostSplit
    cancellation_notice_hours: int
    foul_caller_note: str | None = None
    extra_rules: str | None = None


def default_terms(kickoff: datetime, referee: RefereeMode, place: PlaceKind, place_note: str | None) -> ContractTerms:
    return ContractTerms(
        kickoff_at=kickoff, duration_minutes=60, referee_mode=referee, place_kind=place, place_note=place_note,
        host_kit_color="Oscuro", guest_kit_color="Claro", substitutions=None, field_cost_split=CostSplit.HALF,
        referee_cost_split=CostSplit.HALF, cancellation_notice_hours=24,
    )


def _check(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise DomainError(code, message)


def validate_terms(terms: ContractTerms, now: datetime) -> None:
    _check(terms.kickoff_at > now, "KICKOFF_IN_PAST", "La hora del partido ya pasó. Elige una hora futura.")
    _check(terms.kickoff_at - now <= MAX_AHEAD, "KICKOFF_TOO_FAR", "El partido debe ser en los próximos 60 días.")
    _check(20 <= terms.duration_minutes <= 240, "DURATION_OUT_OF_RANGE", "La duración va de 20 a 240 minutos.")
    _check(terms.substitutions is None or 0 <= terms.substitutions <= 30, "SUBSTITUTIONS_OUT_OF_RANGE",
           "Los cambios van de 0 a 30, o ilimitados.")
    _check(0 <= terms.cancellation_notice_hours <= 72, "NOTICE_OUT_OF_RANGE",
           "El aviso de cancelación va de 0 a 72 horas.")
    host, guest = terms.host_kit_color.strip(), terms.guest_kit_color.strip()
    _check(bool(host) and bool(guest), "KIT_COLOR_REQUIRED", "Indica el color de uniforme de cada equipo.")
    _check(host.casefold() != guest.casefold(), "KIT_COLORS_CLASH", "Los uniformes deben ser de colores distintos.")
    _check(terms.referee_mode != RefereeMode.EITHER, "REFEREE_MODE_REQUIRED",
           "Indica si el partido es con o sin árbitro.")
    _check(terms.referee_mode == RefereeMode.WITHOUT or not terms.foul_caller_note,
           "FOUL_CALLER_ONLY_WITHOUT_REFEREE", "Quién cobra las faltas solo se pacta en partidos sin árbitro.")


def terms_to_dict(terms: ContractTerms) -> dict[str, Any]:
    data = asdict(terms)
    data["kickoff_at"] = terms.kickoff_at.isoformat()
    return {k: (v.value if isinstance(v, StrEnum) else v) for k, v in data.items()}


def terms_from_dict(data: dict[str, Any]) -> ContractTerms:
    return ContractTerms(
        **{**data, "kickoff_at": datetime.fromisoformat(data["kickoff_at"]),
           "referee_mode": RefereeMode(data["referee_mode"]), "place_kind": PlaceKind(data["place_kind"]),
           "field_cost_split": CostSplit(data["field_cost_split"]),
           "referee_cost_split": CostSplit(data["referee_cost_split"])}
    )


def diff_terms(old: ContractTerms, new: ContractTerms) -> dict[str, dict[str, Any]]:
    before, after = terms_to_dict(old), terms_to_dict(new)
    changed = [f.name for f in fields(ContractTerms) if before[f.name] != after[f.name]]
    return {"before": {k: before[k] for k in changed}, "after": {k: after[k] for k in changed}}
