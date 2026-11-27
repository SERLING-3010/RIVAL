"""Goles con tipo (Sprint 23): ver los del partido y que el rival los confirme o rechace."""

from dataclasses import asdict

from fastapi import APIRouter
from pydantic import AwareDatetime, BaseModel

from app.api.dependencies import CtxDep, UserDep
from app.api.schemas_auth import StrictModel
from app.services import goal_claim_service

router = APIRouter(prefix="/api/v1")


class GoalClaimOut(BaseModel):
    id: int
    team_id: int
    user_id: int
    display_name: str
    kind: str
    status: str
    claimed_at: AwareDatetime
    can_decide: bool


class GoalClaimDecisionBody(StrictModel):
    accept: bool


@router.get("/contracts/{contract_id}/goal-claims")
def list_goal_claims(contract_id: int, ctx: CtxDep, user: UserDep) -> list[GoalClaimOut]:
    return [GoalClaimOut.model_validate(asdict(v)) for v in goal_claim_service.claims(ctx, user, contract_id)]


@router.post("/goal-claims/{claim_id}/decision")
def decide_goal_claim(claim_id: int, body: GoalClaimDecisionBody, ctx: CtxDep, user: UserDep) -> dict[str, str]:
    claim = goal_claim_service.decide(ctx, user, claim_id, body.accept)
    return {"status": claim.status}
