"""Rutas de la alineación táctica (Sprint 19). Solo el equipo propio la ve; el rival nunca."""

from dataclasses import asdict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.api.dependencies import CtxDep, UserDep
from app.api.schemas_auth import StrictModel
from app.services import tactics_service
from app.services.tactics_service import TacticView

router = APIRouter(prefix="/api/v1")


class StarterIn(StrictModel):
    user_id: int
    position: str = Field(max_length=40)


class TacticBody(StrictModel):
    formation: str | None = Field(default=None, max_length=15)
    starters: list[StarterIn] = Field(max_length=11)
    subs: list[int] = Field(default_factory=list, max_length=12)


class SlotOut(BaseModel):
    user_id: int
    display_name: str
    position: str | None
    still_going: bool


class TacticOut(BaseModel):
    contract_id: int
    team_id: int
    players_per_side: int
    uses_formation: bool
    suggested_formations: list[str]
    formation: str | None
    starters: list[SlotOut]
    subs: list[SlotOut]
    eligible: list[SlotOut]
    can_edit: bool


def _out(view: TacticView) -> TacticOut:
    return TacticOut.model_validate(asdict(view))


@router.get("/contracts/{contract_id}/tactics")
def get_tactics(contract_id: int, ctx: CtxDep, user: UserDep) -> TacticOut:
    return _out(tactics_service.view(ctx, user, contract_id))


@router.post("/contracts/{contract_id}/tactics")
def save_tactics(contract_id: int, body: TacticBody, ctx: CtxDep, user: UserDep) -> TacticOut:
    starters = [(s.user_id, s.position) for s in body.starters]
    return _out(tactics_service.save(ctx, user, contract_id, body.formation, starters, body.subs))
