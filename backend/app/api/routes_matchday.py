"""Rutas del día del partido (Sprint 10): convocatoria y valoraciones entre compañeros."""

from dataclasses import asdict

from fastapi import APIRouter
from pydantic import AwareDatetime, BaseModel, Field

from app.api.dependencies import CtxDep, UserDep
from app.api.schemas_auth import StrictModel
from app.persistence.models_identity import UserAccount
from app.services import callup_service, player_rating_service
from app.services.context import ServiceContext

router = APIRouter(prefix="/api/v1")


class CallUpBody(StrictModel):
    user_ids: list[int] = Field(min_length=1, max_length=40)


class RespondBody(StrictModel):
    going: bool


class RatingBody(StrictModel):
    rated_id: int
    score: int = Field(ge=1, le=10)


class CallUpItemOut(BaseModel):
    user_id: int
    display_name: str
    status: str


class TeamCallUpOut(BaseModel):
    contract_id: int
    items: list[CallUpItemOut]
    going: int
    not_going: int
    pending: int


class MyCallUpOut(BaseModel):
    contract_id: int
    my_team: str
    opponent: str
    kickoff_at: AwareDatetime
    status: str


class RateableOut(BaseModel):
    user_id: int
    display_name: str


def _team(ctx: ServiceContext, user: UserAccount, contract_id: int) -> TeamCallUpOut:
    return TeamCallUpOut.model_validate(asdict(callup_service.team_callup(ctx, user, contract_id)))


def _pending(ctx: ServiceContext, user: UserAccount, contract_id: int) -> list[RateableOut]:
    return [RateableOut.model_validate(asdict(r)) for r in player_rating_service.to_rate(ctx, user, contract_id)]


@router.get("/contracts/{contract_id}/callup")
def get_callup(contract_id: int, ctx: CtxDep, user: UserDep) -> TeamCallUpOut:
    return _team(ctx, user, contract_id)


@router.post("/contracts/{contract_id}/callup")
def send_callup(contract_id: int, body: CallUpBody, ctx: CtxDep, user: UserDep) -> TeamCallUpOut:
    callup_service.call_up(ctx, user, contract_id, body.user_ids)
    return _team(ctx, user, contract_id)


@router.post("/contracts/{contract_id}/callup/respond")
def respond_callup(contract_id: int, body: RespondBody, ctx: CtxDep, user: UserDep) -> TeamCallUpOut:
    callup_service.respond(ctx, user, contract_id, body.going)
    return _team(ctx, user, contract_id)


@router.get("/me/callups")
def my_callups(ctx: CtxDep, user: UserDep) -> list[MyCallUpOut]:
    return [MyCallUpOut.model_validate(asdict(c)) for c in callup_service.my_callups(ctx, user)]


@router.get("/contracts/{contract_id}/ratings/pending")
def pending_ratings(contract_id: int, ctx: CtxDep, user: UserDep) -> list[RateableOut]:
    return _pending(ctx, user, contract_id)


@router.post("/contracts/{contract_id}/ratings", status_code=201)
def rate_player(contract_id: int, body: RatingBody, ctx: CtxDep, user: UserDep) -> list[RateableOut]:
    player_rating_service.rate(ctx, user, contract_id, body.rated_id, body.score)
    return _pending(ctx, user, contract_id)

