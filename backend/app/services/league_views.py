"""Entradas y vistas de ligas (Sprint 5). Nunca incluyen correos ni datos personales."""

from dataclasses import dataclass, field
from datetime import datetime

from app.services.team_views import TeamSummaryView


@dataclass
class LeagueInput:
    name: str
    sport_code: str
    modality_code: str
    city: str
    season: str
    description: str | None = None


@dataclass
class LeagueSearchInput:
    sport_code: str | None = None
    city: str | None = None
    query: str | None = None
    page: int = 1
    page_size: int = field(default=20)


@dataclass(frozen=True)
class LeagueSummaryView:
    id: int
    name: str
    sport_code: str
    modality_code: str
    city: str
    season: str
    team_count: int
    referee_count: int


@dataclass(frozen=True)
class StaffView:
    user_id: int
    display_name: str
    role: str


@dataclass(frozen=True)
class TeamEntryView:
    id: int
    team: TeamSummaryView
    status: str


@dataclass(frozen=True)
class RefereeEntryView:
    id: int
    user_id: int
    display_name: str
    status: str


@dataclass(frozen=True)
class LeagueDetailView:
    league: LeagueSummaryView
    description: str | None
    my_role: str | None  # rol del usuario en el personal de la liga, si tiene
    transfer_window_start: datetime | None  # ventana de traspasos (Sprint 13); None = siempre abierta
    transfer_window_end: datetime | None
    staff: list[StaffView]
    teams: list[TeamEntryView]
    referees: list[RefereeEntryView]
    pending_teams: list[TeamEntryView]  # solo para el personal
    pending_referees: list[RefereeEntryView]  # solo para el personal
    my_team_requests: list[TeamEntryView]  # pendientes o aprobadas de equipos que administro
    my_referee_request: RefereeEntryView | None  # mi solicitud al cuerpo arbitral, si es pendiente o aprobada
    champion: TeamSummaryView | None = None  # Sprint 23: campeón al cerrar la temporada
    closed_at: datetime | None = None


@dataclass(frozen=True)
class LeaguePage:
    items: list[LeagueSummaryView]
    page: int
    page_size: int
    total: int


@dataclass(frozen=True)
class MyLeagueView:
    league: LeagueSummaryView
    relation: str  # ORGANIZER, CO_ORGANIZER, REFEREE_COORDINATOR, REFEREE o TEAM
