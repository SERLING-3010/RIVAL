"""Rutas de rivales sugeridos con motivos (Sprint 18)."""

from dataclasses import asdict

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.dependencies import CtxDep, UserDep
from app.api.schemas_teams import TeamSummaryOut
from app.services import suggestion_service

router = APIRouter(prefix="/api/v1")


class SuggestionOut(BaseModel):
    team: TeamSummaryOut
    distance_band: str | None
    level: int | None
    reasons: list[str]


@router.get("/teams/{team_id}/suggestions")
def suggestions(team_id: int, ctx: CtxDep, user: UserDep) -> list[SuggestionOut]:
    return [SuggestionOut.model_validate(asdict(s)) for s in suggestion_service.rivals_for(ctx, user, team_id)]
