"""Esquemas del calendario, la tabla y los árbitros de partidos de liga (Sprint 8)."""

from pydantic import AwareDatetime, BaseModel, Field

from app.api.schemas_auth import StrictModel
from app.api.schemas_teams import TeamSummaryOut


class FixtureBody(StrictModel):
    first_kickoff: AwareDatetime
    days_between: int = Field(ge=1, le=14)


class AssignRefereeBody(StrictModel):
    referee_id: int


class RefereeScoreBody(StrictModel):
    host_score: int = Field(ge=0, le=9999)
    guest_score: int = Field(ge=0, le=9999)


class FixtureOut(BaseModel):
    round: int
    contract_id: int
    host: TeamSummaryOut
    guest: TeamSummaryOut
    kickoff_at: AwareDatetime
    status: str
    result: str | None


class StandingOut(BaseModel):
    team_id: int
    name: str
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int


class RefereeMatchOut(BaseModel):
    assignment_id: int
    contract_id: int
    status: str
    league_name: str
    host_name: str
    guest_name: str
    kickoff_at: AwareDatetime
    place_kind: str
    place_note: str | None
    result_status: str | None
    host_score: int | None
    guest_score: int | None
