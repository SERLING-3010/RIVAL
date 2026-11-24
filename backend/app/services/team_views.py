"""Vistas de lectura de equipos. Nunca incluyen correo, fecha de nacimiento ni ubicación exacta."""

from dataclasses import dataclass

from app.domain.roles import TeamRole


@dataclass(frozen=True)
class TeamSummaryView:
    id: int
    name: str
    sport_code: str
    modality_code: str
    city: str
    neighborhood: str
    member_count: int
    has_coach: bool


@dataclass(frozen=True)
class MemberItem:
    user_id: int
    display_name: str
    role: TeamRole
    position: str | None


@dataclass(frozen=True)
class TeamDetailView:
    team: TeamSummaryView
    admin_user_id: int | None
    members: list[MemberItem]


@dataclass(frozen=True)
class MyTeamView:
    team: TeamSummaryView
    my_role: TeamRole
    is_admin: bool
    pending_requests: int


@dataclass(frozen=True)
class TeamPage:
    items: list[TeamSummaryView]
    page: int
    page_size: int
    total: int


@dataclass(frozen=True)
class JoinRequestView:
    id: int
    team_id: int
    user_id: int
    display_name: str
    position: str | None
    desired_role: TeamRole
    message: str | None
    status: str
