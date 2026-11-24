"""Rutas de ligas: crear, buscar, detalle, personal, inscripción de equipos y cuerpo arbitral."""

from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.dependencies import CtxDep, UserDep
from app.api.schemas_leagues import (
    CreateLeagueBody, LeagueDetailOut, LeaguePageOut, MyLeagueOut, StaffBody, TeamRequestBody,
)
from app.domain.league_rules import EnrollmentKind
from app.persistence.models_identity import UserAccount
from app.services import league_enrollment_service, league_queries, league_service
from app.services.context import ServiceContext
from app.services.league_views import LeagueInput, LeagueSearchInput

router = APIRouter(prefix="/api/v1")


def _detail(ctx: ServiceContext, user: UserAccount, league_id: int) -> LeagueDetailOut:
    return LeagueDetailOut.model_validate(asdict(league_queries.league_detail(ctx, user, league_id)))


@router.post("/leagues", status_code=201)
def create_league(body: CreateLeagueBody, ctx: CtxDep, user: UserDep) -> LeagueDetailOut:
    league = league_service.create_league(ctx, user, LeagueInput(**body.model_dump()))
    return _detail(ctx, user, league.id)


@router.get("/leagues")
def search_leagues(
    ctx: CtxDep,
    _user: UserDep,
    sport: Annotated[str | None, Query(max_length=30)] = None,
    city: Annotated[str | None, Query(max_length=60)] = None,
    q: Annotated[str | None, Query(max_length=60)] = None,
    page: Annotated[int, Query(ge=1, le=1000)] = 1,
) -> LeaguePageOut:
    result = league_queries.search_leagues(ctx, LeagueSearchInput(sport_code=sport, city=city, query=q, page=page))
    return LeaguePageOut.model_validate(asdict(result))


@router.get("/me/leagues")
def my_leagues(ctx: CtxDep, user: UserDep) -> list[MyLeagueOut]:
    return [MyLeagueOut.model_validate(asdict(v)) for v in league_queries.my_leagues(ctx, user)]


@router.get("/leagues/{league_id}")
def league_detail(league_id: int, ctx: CtxDep, user: UserDep) -> LeagueDetailOut:
    return _detail(ctx, user, league_id)


@router.post("/leagues/{league_id}/staff", status_code=201)
def add_staff(league_id: int, body: StaffBody, ctx: CtxDep, user: UserDep) -> LeagueDetailOut:
    league_service.add_staff(ctx, user, league_id, body.user_id, body.role)
    return _detail(ctx, user, league_id)


@router.post("/leagues/{league_id}/team-requests", status_code=201)
def request_team(league_id: int, body: TeamRequestBody, ctx: CtxDep, user: UserDep) -> LeagueDetailOut:
    league_enrollment_service.request_team(ctx, user, league_id, body.team_id)
    return _detail(ctx, user, league_id)


@router.post("/leagues/{league_id}/referee-requests", status_code=201)
def request_referee(league_id: int, ctx: CtxDep, user: UserDep) -> LeagueDetailOut:
    league_enrollment_service.request_referee(ctx, user, league_id)
    return _detail(ctx, user, league_id)


@router.post("/league-requests/{kind}/{entry_id}/approve")
def approve(kind: EnrollmentKind, entry_id: int, ctx: CtxDep, user: UserDep) -> LeagueDetailOut:
    entry = league_enrollment_service.decide(ctx, user, kind, entry_id, approve=True)
    return _detail(ctx, user, entry.league_id)


@router.post("/league-requests/{kind}/{entry_id}/reject")
def reject(kind: EnrollmentKind, entry_id: int, ctx: CtxDep, user: UserDep) -> LeagueDetailOut:
    entry = league_enrollment_service.decide(ctx, user, kind, entry_id, approve=False)
    return _detail(ctx, user, entry.league_id)


@router.post("/league-requests/{kind}/{entry_id}/withdraw")
def withdraw(kind: EnrollmentKind, entry_id: int, ctx: CtxDep, user: UserDep) -> LeagueDetailOut:
    entry = league_enrollment_service.withdraw(ctx, user, kind, entry_id)
    return _detail(ctx, user, entry.league_id)
