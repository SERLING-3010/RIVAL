"""Rutas del calendario y la tabla de la liga, y de los árbitros asignados a sus partidos (Sprint 8)."""

from dataclasses import asdict

from fastapi import APIRouter

from app.api.dependencies import CtxDep, UserDep
from app.api.schemas_league_matches import (
    AssignRefereeBody, FixtureBody, FixtureOut, RefereeMatchOut, RefereeScoreBody, StandingOut,
)
from app.persistence.models_identity import UserAccount
from app.services import fixture_service, referee_service, standings_queries
from app.services.context import ServiceContext

router = APIRouter(prefix="/api/v1")


def _calendar(ctx: ServiceContext, league_id: int) -> list[FixtureOut]:
    return [FixtureOut.model_validate(asdict(f)) for f in standings_queries.calendar(ctx, league_id)]


def _mine(ctx: ServiceContext, user: UserAccount) -> list[RefereeMatchOut]:
    return [RefereeMatchOut.model_validate(asdict(m)) for m in referee_service.my_matches(ctx, user)]


@router.post("/leagues/{league_id}/fixtures", status_code=201)
def generate_fixtures(league_id: int, body: FixtureBody, ctx: CtxDep, user: UserDep) -> list[FixtureOut]:
    fixture_service.generate(ctx, user, league_id, body.first_kickoff, body.days_between)
    return _calendar(ctx, league_id)


@router.get("/leagues/{league_id}/calendar")
def calendar(league_id: int, ctx: CtxDep, _user: UserDep) -> list[FixtureOut]:
    return _calendar(ctx, league_id)


@router.get("/leagues/{league_id}/table")
def table(league_id: int, ctx: CtxDep, _user: UserDep) -> list[StandingOut]:
    return [StandingOut.model_validate(asdict(r)) for r in standings_queries.table(ctx, league_id)]


@router.post("/contracts/{contract_id}/referee", status_code=201)
def assign_referee(contract_id: int, body: AssignRefereeBody, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    assignment = referee_service.assign(ctx, user, contract_id, body.referee_id)
    return {"assignment_id": assignment.id, "status": assignment.status}


@router.get("/me/referee-matches")
def my_referee_matches(ctx: CtxDep, user: UserDep) -> list[RefereeMatchOut]:
    return _mine(ctx, user)


@router.post("/referee-assignments/{assignment_id}/accept")
def accept_assignment(assignment_id: int, ctx: CtxDep, user: UserDep) -> list[RefereeMatchOut]:
    referee_service.respond(ctx, user, assignment_id, accept=True)
    return _mine(ctx, user)


@router.post("/referee-assignments/{assignment_id}/decline")
def decline_assignment(assignment_id: int, ctx: CtxDep, user: UserDep) -> list[RefereeMatchOut]:
    referee_service.respond(ctx, user, assignment_id, accept=False)
    return _mine(ctx, user)


@router.post("/contracts/{contract_id}/referee-result")
def referee_result(contract_id: int, body: RefereeScoreBody, ctx: CtxDep, user: UserDep) -> list[RefereeMatchOut]:
    referee_service.report_result(ctx, user, contract_id, body.host_score, body.guest_score)
    return _mine(ctx, user)
