"""Esquemas del contrato de partido (Sprint 3), resultado y actividad (Sprint 4)."""

from typing import Any

from pydantic import AwareDatetime, BaseModel, Field

from app.api.schemas_auth import StrictModel
from app.api.schemas_teams import TeamSummaryOut
from app.api.schemas_venues import BookingOut
from app.domain.contract_rules import CostSplit
from app.domain.match_rules import PlaceKind, RefereeMode


class ContractTermsBody(StrictModel):
    kickoff_at: AwareDatetime
    duration_minutes: int = Field(ge=1, le=1000)
    referee_mode: RefereeMode
    place_kind: PlaceKind
    place_note: str | None = Field(default=None, max_length=120)
    host_kit_color: str = Field(max_length=30)
    guest_kit_color: str = Field(max_length=30)
    substitutions: int | None = Field(default=None, ge=0, le=99)
    field_cost_split: CostSplit
    referee_cost_split: CostSplit
    cancellation_notice_hours: int = Field(ge=0, le=999)
    foul_caller_note: str | None = Field(default=None, max_length=120)
    extra_rules: str | None = Field(default=None, max_length=300)


class ProposalBody(StrictModel):
    base_version: int = Field(ge=1)
    terms: ContractTermsBody
    note: str | None = Field(default=None, max_length=200)


class VersionBody(StrictModel):
    version: int = Field(ge=1)


class CancelBody(StrictModel):
    reason: str = Field(max_length=200)


class ScoreBody(StrictModel):
    host_score: int = Field(ge=0, le=9999)
    guest_score: int = Field(ge=0, le=9999)


class ContractTermsOut(BaseModel):
    kickoff_at: AwareDatetime
    duration_minutes: int
    referee_mode: str
    place_kind: str
    place_note: str | None
    host_kit_color: str
    guest_kit_color: str
    substitutions: int | None
    field_cost_split: str
    referee_cost_split: str
    cancellation_notice_hours: int
    foul_caller_note: str | None
    extra_rules: str | None


class VersionOut(BaseModel):
    version: int
    terms: ContractTermsOut
    proposed_by_side: str | None
    note: str | None
    created_at: AwareDatetime
    signed_by: list[str]


class ResultReportOut(BaseModel):
    side: str
    host_score: int
    guest_score: int
    reported_at: AwareDatetime


class ResultOut(BaseModel):
    status: str
    host_score: int | None
    guest_score: int | None
    reports: list[ResultReportOut]
    by_referee: bool


class RefereeOut(BaseModel):
    assignment_id: int
    referee_id: int
    display_name: str
    status: str


class ContractOut(BaseModel):
    id: int
    request_id: int | None
    league_id: int | None
    host: TeamSummaryOut
    guest: TeamSummaryOut
    status: str
    my_side: str
    is_admin: bool
    current: VersionOut
    signed: VersionOut | None
    versions: list[VersionOut]
    cancel_reason: str | None
    result: ResultOut | None
    booking: BookingOut | None
    ready_to_play: bool
    referee: RefereeOut | None


class ContractSummaryOut(BaseModel):
    id: int
    host: TeamSummaryOut
    guest: TeamSummaryOut
    status: str
    kickoff_at: AwareDatetime
    my_side: str
    awaiting_my_signature: bool
    result_status: str | None
    host_score: int | None
    guest_score: int | None


class ActivityOut(BaseModel):
    occurred_at: AwareDatetime
    action: str
    entity: str
    entity_id: str
    actor_type: str
    actor_name: str | None
    approver_name: str | None
    before: dict[str, Any] | None
    after: dict[str, Any] | None
