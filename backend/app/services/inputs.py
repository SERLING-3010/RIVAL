"""Datos de entrada de los casos de uso (ya validados en forma por la API)."""

from dataclasses import dataclass, field
from datetime import date

from app.domain.roles import TeamRole, UserRole


@dataclass
class RegisterInput:
    email: str
    password: str
    display_name: str
    birth_date: date
    role: UserRole
    sports: list[str]
    city: str
    neighborhood: str
    position: str | None = None


@dataclass
class CreateTeamInput:
    name: str
    sport_code: str
    modality_code: str
    city: str
    neighborhood: str
    as_coach: bool = False


@dataclass
class JoinRequestInput:
    desired_role: TeamRole = TeamRole.PLAYER
    message: str | None = None


@dataclass
class TeamSearchInput:
    sport_code: str | None = None
    modality_code: str | None = None
    city: str | None = None
    query: str | None = None
    page: int = 1
    page_size: int = field(default=20)
