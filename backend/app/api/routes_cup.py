"""Rutas de la copa eliminatoria de una liga (Sprint 16)."""

from dataclasses import asdict

from fastapi import APIRouter
from pydantic import AwareDatetime, BaseModel

from app.api.dependencies import CtxDep, UserDep
from app.api.schemas_auth import StrictModel
from app.api.schemas_league_matches import FixtureBody
from app.services import cup_queries, cup_service

router = APIRouter(prefix="/api/v1")


class TiebreakBody(StrictModel):
    winner_team_id: int


class CupMatchOut(BaseModel):
    id: int
    position: int
    host_team_id: int | None
    guest_team_id: int | None
    host_name: str | None
    guest_name: str | None
    contract_id: int | None
    host_score: int | None
    guest_score: int | None
    winner_name: str | None
    needs_tiebreak: bool


class CupRoundOut(BaseModel):
    number: int
    name: str
    planned_at: AwareDatetime
    matches: list[CupMatchOut]


class CupOut(BaseModel):
    league_id: int
    champion_name: str | None
    can_manage: bool
    rounds: list[CupRoundOut]


@router.get("/leagues/{league_id}/cup")
def get_cup(league_id: int, ctx: CtxDep, user: UserDep) -> CupOut:
    return CupOut.model_validate(asdict(cup_queries.bracket(ctx, user, league_id)))


@router.post("/leagues/{league_id}/cup", status_code=201)
def create_cup(league_id: int, body: FixtureBody, ctx: CtxDep, user: UserDep) -> CupOut:
    cup_service.create(ctx, user, league_id, body.first_kickoff, body.days_between)
    return get_cup(league_id, ctx, user)


@router.post("/cup-matches/{cup_match_id}/tiebreak")
def set_tiebreak(cup_match_id: int, body: TiebreakBody, ctx: CtxDep, user: UserDep) -> dict[str, int]:
    match = cup_service.set_tiebreak(ctx, user, cup_match_id, body.winner_team_id)
    return {"id": match.id}
