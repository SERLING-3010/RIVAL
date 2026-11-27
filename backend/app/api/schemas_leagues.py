"""Esquemas de ligas y cuerpo arbitral (Sprint 5)."""

from pydantic import AwareDatetime, BaseModel, Field

from app.api.schemas_auth import StrictModel
from app.api.schemas_teams import TeamSummaryOut
from app.domain.league_rules import StaffRole


class CreateLeagueBody(StrictModel):
    name: str = Field(max_length=80)
    sport_code: str = Field(max_length=30)
    modality_code: str = Field(max_length=30)
    city: str = Field(max_length=60)
    season: str = Field(max_length=10)
    description: str | None = Field(default=None, max_length=300)


class TeamRequestBody(StrictModel):
    team_id: int


class StaffBody(StrictModel):
    user_id: int
    role: StaffRole


class LeagueSummaryOut(BaseModel):
    id: int
    name: str
    sport_code: str
    modality_code: str
    city: str
    season: str
    team_count: int
    referee_count: int


class LeaguePageOut(BaseModel):
    items: list[LeagueSummaryOut]
    page: int
    page_size: int
    total: int


class StaffOut(BaseModel):
    user_id: int
    display_name: str
    role: str


class TeamEntryOut(BaseModel):
    id: int
    team: TeamSummaryOut
    status: str


class RefereeEntryOut(BaseModel):
    id: int
    user_id: int
    display_name: str
    status: str


class LeagueDetailOut(BaseModel):
    league: LeagueSummaryOut
    description: str | None
    my_role: str | None
    transfer_window_start: AwareDatetime | None
    transfer_window_end: AwareDatetime | None
    staff: list[StaffOut]
    teams: list[TeamEntryOut]
    referees: list[RefereeEntryOut]
    pending_teams: list[TeamEntryOut]
    pending_referees: list[RefereeEntryOut]
    my_team_requests: list[TeamEntryOut]
    my_referee_request: RefereeEntryOut | None
    champion: TeamSummaryOut | None = None
    closed_at: AwareDatetime | None = None


class MyLeagueOut(BaseModel):
    league: LeagueSummaryOut
    relation: str
