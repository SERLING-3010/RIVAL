"""Reglas de ligas y cuerpo arbitral (Sprint 5, RIV-010 y RIV-011).

La liga la administra quien la crea (organizador) y puede nombrar coorganizadores y un
coordinador arbitral (Sprint 0, 4.2.1).
"""

import re
from enum import StrEnum
from typing import Literal

from app.domain.errors import DomainError, PermissionDeniedError

_SEASON = re.compile(r"^\d{4}(-[12])?$")


class StaffRole(StrEnum):
    ORGANIZER = "ORGANIZER"
    CO_ORGANIZER = "CO_ORGANIZER"
    REFEREE_COORDINATOR = "REFEREE_COORDINATOR"


class EnrollmentStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


ACTIVE_STATUSES = (EnrollmentStatus.PENDING.value, EnrollmentStatus.APPROVED.value)
EnrollmentKind = Literal["team", "referee"]

_DECIDERS: dict[str, frozenset[StaffRole]] = {
    "team": frozenset({StaffRole.ORGANIZER, StaffRole.CO_ORGANIZER}),
    "referee": frozenset({StaffRole.ORGANIZER, StaffRole.CO_ORGANIZER, StaffRole.REFEREE_COORDINATOR}),
}


def validate_league_name(name: str) -> str:
    clean = " ".join(name.split())
    if not 3 <= len(clean) <= 60:
        raise DomainError("INVALID_LEAGUE_NAME", "El nombre de la liga debe tener entre 3 y 60 caracteres.")
    return clean


def validate_season(season: str) -> str:
    clean = season.strip()
    if not _SEASON.match(clean):
        raise DomainError("INVALID_SEASON", "Escribe la temporada como 2026, 2026-1 o 2026-2.")
    return clean


def check_can_create(is_referee: bool, has_team: bool) -> None:
    if not (is_referee or has_team):
        raise PermissionDeniedError(
            "LEAGUE_CREATOR_NOT_ALLOWED", "Para crear una liga debes tener equipo o el rol de árbitro."
        )


def check_can_decide(role: StaffRole | None, kind: EnrollmentKind) -> None:
    if role is None or role not in _DECIDERS[kind]:
        who = "el organizador o un coorganizador" if kind == "team" else "el organizador o el coordinador arbitral"
        raise PermissionDeniedError("LEAGUE_STAFF_ONLY", f"Solo {who} puede decidir esta solicitud.")
