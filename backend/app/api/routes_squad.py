"""Ruta de la plantilla del equipo en modo juego (Sprints 22 y 23). Solo para miembros del equipo."""

from dataclasses import asdict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.api.dependencies import CtxDep, UserDep
from app.api.schemas_manager import SpecialCardOut
from app.api.schemas_teams import TeamSummaryOut
from app.api.schemas_auth import StrictModel
from app.services import squad_queries, team_look_service

router = APIRouter(prefix="/api/v1")


class SquadCardOut(BaseModel):
    user_id: int
    display_name: str
    position: str | None
    role: str
    media: int
    tier: str
    matches: int
    goals: int
    wins: int
    rating_average: float | None
    hat_tricks: int
    badges: int


class StarterOut(BaseModel):
    user_id: int
    position: str | None


class TeamCardOut(BaseModel):
    tier: str
    next_tier: str | None
    media_to_next: int
    display_tier: str
    chosen: str | None
    available: list[str]
    goals: int
    clean_sheets: int
    cups: int
    leagues: int
    specials: list[SpecialCardOut]


class SquadOut(BaseModel):
    team: TeamSummaryOut
    media: int | None
    wins: int
    draws: int
    losses: int
    level: int | None
    badges: list[str]
    players_per_side: int
    formation: str | None
    suggested: bool
    starters: list[StarterOut]
    subs: list[int]
    members: list[SquadCardOut]
    card: TeamCardOut | None
    crest: str | None
    can_edit: bool


@router.get("/teams/{team_id}/squad")
def team_squad(team_id: int, ctx: CtxDep, user: UserDep) -> SquadOut:
    return SquadOut.model_validate(asdict(squad_queries.squad(ctx, user, team_id)))


class CardChoiceBody(StrictModel):
    choice: str | None = Field(default=None, max_length=20)  # código, "BASIC" o null (automático)


class CrestBody(StrictModel):
    crest: str | None = Field(default=None, max_length=40)  # "FORMA|#color|#color|SÍMBOLO" o null


@router.post("/teams/{team_id}/card-choice")
def choose_team_design(team_id: int, body: CardChoiceBody, ctx: CtxDep, user: UserDep) -> SquadOut:
    team_look_service.set_card_choice(ctx, user, team_id, body.choice)
    return team_squad(team_id, ctx, user)


@router.post("/teams/{team_id}/crest")
def change_team_crest(team_id: int, body: CrestBody, ctx: CtxDep, user: UserDep) -> SquadOut:
    team_look_service.set_crest(ctx, user, team_id, body.crest)
    return team_squad(team_id, ctx, user)
