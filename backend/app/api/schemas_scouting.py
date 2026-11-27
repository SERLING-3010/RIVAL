"""Esquemas de rivales, agentes libres, invitaciones y partidos (Sprint 2)."""

from pydantic import AwareDatetime, BaseModel, Field

from app.api.schemas_auth import StrictModel
from app.api.schemas_teams import TeamSummaryOut
from app.domain.geo import DistanceBand
from app.domain.match_rules import PlaceKind, RefereeMode


class RivalOut(BaseModel):
    team: TeamSummaryOut
    distance_band: DistanceBand | None
    level: int | None
    level_reliable: bool


class RivalPageOut(BaseModel):
    items: list[RivalOut]
    page: int
    page_size: int
    total: int


class FreeAgentRequest(StrictModel):
    sport_code: str = Field(max_length=30)
    active: bool
    position: str | None = Field(default=None, max_length=40)
    note: str | None = Field(default=None, max_length=200)


class FreeAgentProfileOut(BaseModel):
    sport_code: str
    active: bool
    position: str | None
    note: str | None


class FreeAgentOut(BaseModel):
    user_id: int
    display_name: str
    sport_code: str
    position: str | None
    note: str | None
    neighborhood: str
    city: str


class FreeAgentPageOut(BaseModel):
    items: list[FreeAgentOut]
    page: int
    page_size: int
    total: int


class InviteRequest(StrictModel):
    user_id: int
    message: str | None = Field(default=None, max_length=200)


class InvitationOut(BaseModel):
    id: int
    team: TeamSummaryOut
    message: str | None


class MatchRequestBody(StrictModel):
    window_start: AwareDatetime
    window_end: AwareDatetime
    scope: str = Field(pattern="^(NEARBY|NEIGHBORHOOD|CITY)$")
    radius_km: int | None = Field(default=None, ge=1, le=15)
    target_team_id: int | None = None
    referee_mode: RefereeMode
    place_kind: PlaceKind
    place_note: str | None = Field(default=None, max_length=120)
    message: str | None = Field(default=None, max_length=200)


class OfferBody(StrictModel):
    proposed_start: AwareDatetime
    referee_mode: RefereeMode
    place_kind: PlaceKind
    place_note: str | None = Field(default=None, max_length=120)
    message: str | None = Field(default=None, max_length=200)


class MatchRequestOut(BaseModel):
    id: int
    team: TeamSummaryOut
    target_team_id: int | None
    scope: str
    radius_km: int | None
    window_start: AwareDatetime
    window_end: AwareDatetime
    referee_mode: str
    place_kind: str
    place_note: str | None
    message: str | None
    status: str
    distance_band: DistanceBand | None
    pending_offers: int
    accepted_offer_id: int | None


class OfferOut(BaseModel):
    id: int
    request_id: int
    team: TeamSummaryOut
    version: int
    proposed_start: AwareDatetime
    referee_mode: str
    place_kind: str
    place_note: str | None
    message: str | None
    status: str
