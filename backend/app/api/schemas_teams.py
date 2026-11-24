"""Esquemas de equipos y solicitudes."""

from pydantic import BaseModel, Field

from app.api.schemas_auth import StrictModel
from app.domain.roles import TeamRole


class CreateTeamRequest(StrictModel):
    name: str = Field(max_length=60)
    sport_code: str = Field(max_length=30)
    modality_code: str = Field(max_length=30)
    city: str = Field(max_length=60)
    neighborhood: str = Field(max_length=60)
    as_coach: bool = False


class JoinRequestBody(StrictModel):
    desired_role: TeamRole = TeamRole.PLAYER
    message: str | None = Field(default=None, max_length=200)


class SetCaptainRequest(StrictModel):
    user_id: int


class TeamSummaryOut(BaseModel):
    id: int
    name: str
    sport_code: str
    modality_code: str
    city: str
    neighborhood: str
    member_count: int
    has_coach: bool


class MemberOut(BaseModel):
    user_id: int
    display_name: str
    role: TeamRole
    position: str | None


class TeamDetailOut(BaseModel):
    team: TeamSummaryOut
    admin_user_id: int | None
    members: list[MemberOut]


class MyTeamOut(BaseModel):
    team: TeamSummaryOut
    my_role: TeamRole
    is_admin: bool
    pending_requests: int


class TeamPageOut(BaseModel):
    items: list[TeamSummaryOut]
    page: int
    page_size: int
    total: int


class JoinRequestOut(BaseModel):
    id: int
    team_id: int
    user_id: int
    display_name: str
    position: str | None
    desired_role: TeamRole
    message: str | None
    status: str
