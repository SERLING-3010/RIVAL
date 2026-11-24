"""Rutas de préstamos por un partido y ventanas de traspasos de liga (Sprint 13)."""

from dataclasses import asdict
from typing import Literal

from fastapi import APIRouter
from pydantic import AwareDatetime, BaseModel

from app.api.dependencies import CtxDep, UserDep
from app.api.schemas_auth import StrictModel
from app.services import loan_queries, loan_service, transfer_window_service

router = APIRouter(prefix="/api/v1")


class LoanBody(StrictModel):
    player_id: int
    from_team_id: int


class WindowBody(StrictModel):
    starts_at: AwareDatetime | None = None
    ends_at: AwareDatetime | None = None


class LoanOut(BaseModel):
    id: int
    contract_id: int
    player_id: int
    player_name: str
    from_team: str
    to_team: str
    status: str
    kickoff_at: AwareDatetime


class WindowOut(BaseModel):
    league_id: int
    starts_at: AwareDatetime | None
    ends_at: AwareDatetime | None


@router.get("/contracts/{contract_id}/loans")
def contract_loans(contract_id: int, ctx: CtxDep, user: UserDep) -> list[LoanOut]:
    return [LoanOut.model_validate(asdict(v)) for v in loan_queries.for_contract(ctx, user, contract_id)]


@router.post("/contracts/{contract_id}/loans", status_code=201)
def request_loan(contract_id: int, body: LoanBody, ctx: CtxDep, user: UserDep) -> list[LoanOut]:
    loan_service.request(ctx, user, contract_id, body.player_id, body.from_team_id)
    return contract_loans(contract_id, ctx, user)


@router.get("/me/loans")
def my_loans(ctx: CtxDep, user: UserDep) -> list[LoanOut]:
    return [LoanOut.model_validate(asdict(v)) for v in loan_queries.awaiting_me(ctx, user)]


@router.post("/loans/{loan_id}/{decision}")
def decide_loan(
    loan_id: int,
    decision: Literal["owner-accept", "owner-reject", "player-accept", "player-reject", "cancel"],
    ctx: CtxDep,
    user: UserDep,
) -> dict[str, object]:
    if decision.startswith("owner-"):
        loan = loan_service.decide_owner(ctx, user, loan_id, accept=decision == "owner-accept")
    elif decision.startswith("player-"):
        loan = loan_service.decide_player(ctx, user, loan_id, accept=decision == "player-accept")
    else:
        loan = loan_service.cancel(ctx, user, loan_id)
    return {"id": loan.id, "status": loan.status}


@router.post("/leagues/{league_id}/transfer-window")
def set_window(league_id: int, body: WindowBody, ctx: CtxDep, user: UserDep) -> WindowOut:
    league = transfer_window_service.set_window(ctx, user, league_id, body.starts_at, body.ends_at)
    return WindowOut(league_id=league.id, starts_at=league.transfer_window_start, ends_at=league.transfer_window_end)
