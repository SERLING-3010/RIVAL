"""Rutas de equipos, solicitudes de unión y plantilla. Los permisos se verifican en los servicios."""

from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Query, Response

from app.api.dependencies import CtxDep, UserDep
from app.api.schemas_teams import (
    CreateTeamRequest,
    JoinRequestBody,
    JoinRequestOut,
    MyTeamOut,
    SetCaptainRequest,
    TeamDetailOut,
    TeamPageOut,
)
from app.services import join_service, membership_service, team_service
from app.services.inputs import CreateTeamInput, JoinRequestInput, TeamSearchInput

router = APIRouter(prefix="/api/v1")


def _detail(ctx: CtxDep, team_id: int) -> TeamDetailOut:
    return TeamDetailOut.model_validate(asdict(team_service.team_detail(ctx, team_id)))


@router.post("/teams", status_code=201)
def create_team(body: CreateTeamRequest, ctx: CtxDep, user: UserDep) -> TeamDetailOut:
    team = team_service.create_team(ctx, user, CreateTeamInput(**body.model_dump()))
    return _detail(ctx, team.id)


@router.get("/teams")
def search_teams(
    ctx: CtxDep,
    _user: UserDep,
    sport: Annotated[str | None, Query(max_length=30)] = None,
    modality: Annotated[str | None, Query(max_length=30)] = None,
    city: Annotated[str | None, Query(max_length=60)] = None,
    q: Annotated[str | None, Query(max_length=60)] = None,
    page: Annotated[int, Query(ge=1, le=10_000)] = 1,
    page_size: Annotated[int, Query(ge=1, le=50)] = 20,
) -> TeamPageOut:
    query = TeamSearchInput(sport_code=sport, modality_code=modality, city=city, query=q, page=page, page_size=page_size)
    return TeamPageOut.model_validate(asdict(team_service.search_teams(ctx, query)))


@router.get("/teams/{team_id}")
def team_detail(team_id: int, ctx: CtxDep, _user: UserDep) -> TeamDetailOut:
    return _detail(ctx, team_id)


@router.get("/me/teams")
def my_teams(ctx: CtxDep, user: UserDep) -> list[MyTeamOut]:
    return [MyTeamOut.model_validate(asdict(view)) for view in team_service.my_teams(ctx, user)]


@router.post("/teams/{team_id}/join-requests", status_code=201)
def request_join(team_id: int, body: JoinRequestBody, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    request = join_service.request_join(ctx, user, team_id, JoinRequestInput(**body.model_dump()))
    return {"id": request.id, "status": request.status}


@router.get("/teams/{team_id}/join-requests")
def list_join_requests(team_id: int, ctx: CtxDep, user: UserDep) -> list[JoinRequestOut]:
    return [JoinRequestOut.model_validate(asdict(v)) for v in join_service.list_requests(ctx, user, team_id)]


@router.post("/join-requests/{request_id}/approve")
def approve(request_id: int, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    request = join_service.decide(ctx, user, request_id, approve=True)
    return {"id": request.id, "status": request.status}


@router.post("/join-requests/{request_id}/reject")
def reject(request_id: int, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    request = join_service.decide(ctx, user, request_id, approve=False)
    return {"id": request.id, "status": request.status}


@router.post("/teams/{team_id}/captain")
def set_captain(team_id: int, body: SetCaptainRequest, ctx: CtxDep, user: UserDep) -> TeamDetailOut:
    membership_service.set_captain(ctx, user, team_id, body.user_id)
    return _detail(ctx, team_id)


@router.post("/teams/{team_id}/leave", status_code=204)
def leave(team_id: int, ctx: CtxDep, user: UserDep) -> Response:
    membership_service.leave_team(ctx, user, team_id)
    return Response(status_code=204)
