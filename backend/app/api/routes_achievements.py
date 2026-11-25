"""Rutas de logros e insignias (Sprint 17). Públicas como la ficha del jugador y del equipo."""

from dataclasses import asdict

from fastapi import APIRouter
from pydantic import AwareDatetime, BaseModel

from app.api.dependencies import CtxDep, UserDep
from app.domain.achievement_rules import Badge
from app.services import achievement_queries

router = APIRouter(prefix="/api/v1")


class BadgeOut(BaseModel):
    code: str
    name: str
    description: str
    earned_at: AwareDatetime | None
    progress: str | None


def _out(badges: list[Badge]) -> list[BadgeOut]:
    return [BadgeOut.model_validate(asdict(b)) for b in badges]


@router.get("/players/{user_id}/badges")
def player_badges(user_id: int, ctx: CtxDep, _user: UserDep) -> list[BadgeOut]:
    return _out(achievement_queries.for_player(ctx, user_id))


@router.get("/teams/{team_id}/badges")
def team_badges(team_id: int, ctx: CtxDep, _user: UserDep) -> list[BadgeOut]:
    return _out(achievement_queries.for_team(ctx, team_id))
