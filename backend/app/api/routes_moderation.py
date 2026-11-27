"""Rutas de moderación (Sprint 12): reportes, sanciones, apelaciones y bloqueos entre equipos."""

from dataclasses import asdict

from fastapi import APIRouter
from pydantic import AwareDatetime, BaseModel, Field

from app.api.dependencies import CtxDep, UserDep
from app.api.schemas_auth import StrictModel
from app.api.schemas_teams import TeamSummaryOut
from app.domain.moderation_rules import ReportCategory, SanctionKind
from app.persistence.models_moderation import Sanction
from app.services import appeal_service, block_service, report_service, sanction_service

router = APIRouter(prefix="/api/v1")


class ReportBody(StrictModel):
    category: ReportCategory
    description: str = Field(max_length=600)
    target_user_id: int | None = None
    target_team_id: int | None = None
    contract_id: int | None = None


class NoteBody(StrictModel):
    note: str = Field(max_length=400)


class SanctionBody(StrictModel):
    kind: SanctionKind
    days: int | None = Field(default=None, ge=1, le=365)
    reason: str = Field(max_length=400)


class AppealBody(StrictModel):
    text: str = Field(max_length=600)


class DecideBody(StrictModel):
    revoke: bool


class BlockBody(StrictModel):
    team_id: int


class ReportOut(BaseModel):
    id: int
    category: str
    description: str
    target: str
    created_at: AwareDatetime


class SanctionOut(BaseModel):
    id: int
    kind: str
    reason: str
    ends_at: AwareDatetime | None
    status: str
    created_at: AwareDatetime
    appeal_text: str | None
    appeal_outcome: str | None


class ModerationMeOut(BaseModel):
    is_moderator: bool
    sanctions: list[SanctionOut]


class BlockedOut(BaseModel):
    team: TeamSummaryOut


def _sanction(s: Sanction) -> SanctionOut:
    return SanctionOut(id=s.id, kind=s.kind, reason=s.reason, ends_at=s.ends_at, status=s.status,
                       created_at=s.created_at, appeal_text=s.appeal_text, appeal_outcome=s.appeal_outcome)


@router.post("/reports", status_code=201)
def create_report(body: ReportBody, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    report = report_service.create_report(ctx, user, **body.model_dump())
    return {"id": report.id, "status": report.status}


@router.get("/moderation/me")
def moderation_me(ctx: CtxDep, user: UserDep) -> ModerationMeOut:
    return ModerationMeOut(is_moderator=sanction_service.is_moderator(ctx, user.id),
                           sanctions=[_sanction(s) for s in sanction_service.my_sanctions(ctx, user)])


@router.get("/moderation/reports")
def report_queue(ctx: CtxDep, user: UserDep) -> list[ReportOut]:
    return [ReportOut.model_validate(asdict(r)) for r in sanction_service.queue(ctx, user)]


@router.post("/moderation/reports/{report_id}/dismiss")
def dismiss(report_id: int, body: NoteBody, ctx: CtxDep, user: UserDep) -> list[ReportOut]:
    sanction_service.dismiss(ctx, user, report_id, body.note)
    return report_queue(ctx, user)


@router.post("/moderation/reports/{report_id}/sanction")
def sanction(report_id: int, body: SanctionBody, ctx: CtxDep, user: UserDep) -> list[ReportOut]:
    sanction_service.sanction(ctx, user, report_id, body.kind, body.days, body.reason)
    return report_queue(ctx, user)


@router.post("/sanctions/{sanction_id}/appeal")
def appeal(sanction_id: int, body: AppealBody, ctx: CtxDep, user: UserDep) -> ModerationMeOut:
    appeal_service.appeal(ctx, user, sanction_id, body.text)
    return moderation_me(ctx, user)


@router.get("/moderation/appeals")
def appeals(ctx: CtxDep, user: UserDep) -> list[SanctionOut]:
    return [_sanction(s) for s in appeal_service.appeals_queue(ctx, user)]


@router.post("/moderation/appeals/{sanction_id}/decide")
def decide_appeal(sanction_id: int, body: DecideBody, ctx: CtxDep, user: UserDep) -> list[SanctionOut]:
    appeal_service.decide_appeal(ctx, user, sanction_id, body.revoke)
    return appeals(ctx, user)


@router.get("/teams/{team_id}/blocks")
def blocks(team_id: int, ctx: CtxDep, user: UserDep) -> list[BlockedOut]:
    return [BlockedOut.model_validate(asdict(b)) for b in block_service.blocked_by(ctx, user, team_id)]


@router.post("/teams/{team_id}/blocks", status_code=201)
def block(team_id: int, body: BlockBody, ctx: CtxDep, user: UserDep) -> list[BlockedOut]:
    block_service.block(ctx, user, team_id, body.team_id)
    return blocks(team_id, ctx, user)


@router.post("/teams/{team_id}/blocks/{other_id}/remove")
def unblock(team_id: int, other_id: int, ctx: CtxDep, user: UserDep) -> list[BlockedOut]:
    block_service.unblock(ctx, user, team_id, other_id)
    return blocks(team_id, ctx, user)
