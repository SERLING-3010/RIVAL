"""Rutas de rivales, agentes libres e invitaciones. Las búsquedas tienen límite por usuario."""

from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.api.dependencies import CtxDep, UserDep
from app.api.schemas_scouting import (
    FreeAgentPageOut,
    FreeAgentProfileOut,
    FreeAgentRequest,
    InvitationOut,
    InviteRequest,
    RivalPageOut,
)
from app.domain.geo import DEFAULT_RADIUS_KM, SearchScope
from app.persistence.models_identity import UserAccount
from app.services import free_agent_service, invitation_service, rival_service

router = APIRouter(prefix="/api/v1")


def search_quota(request: Request, ctx: CtxDep, user: UserDep) -> UserAccount:
    """Máximo de búsquedas por usuario: evita adivinar dónde juega un equipo con muchas consultas."""
    request.app.state.search_limiter.hit(f"user:{user.id}", ctx.clock.now())
    return user


SearchUser = Annotated[UserAccount, Depends(search_quota)]


@router.get("/teams/{team_id}/rivals")
def rivals(
    team_id: int, ctx: CtxDep, user: SearchUser,
    scope: SearchScope = SearchScope.CITY,
    radius_km: Annotated[int, Query(ge=1, le=15)] = DEFAULT_RADIUS_KM,
    page: Annotated[int, Query(ge=1, le=1000)] = 1,
    order: Annotated[str, Query(pattern="^(default|level)$")] = "default",
) -> RivalPageOut:
    result = rival_service.search_rivals(ctx, user, team_id, scope, radius_km, page, by_level=order == "level")
    return RivalPageOut.model_validate(asdict(result))


@router.get("/me/free-agent")
def my_free_agent(ctx: CtxDep, user: UserDep) -> list[FreeAgentProfileOut]:
    return [FreeAgentProfileOut.model_validate(p, from_attributes=True)
            for p in free_agent_service.my_profiles(ctx, user)]


@router.post("/me/free-agent")
def set_free_agent(body: FreeAgentRequest, ctx: CtxDep, user: UserDep) -> FreeAgentProfileOut:
    profile = free_agent_service.set_free_agent(ctx, user, body.sport_code, body.active, body.position, body.note)
    return FreeAgentProfileOut.model_validate(profile, from_attributes=True)


@router.get("/free-agents")
def free_agents(
    ctx: CtxDep, user: SearchUser,
    sport: Annotated[str, Query(max_length=30)],
    city: Annotated[str, Query(max_length=60)],
    neighborhood: Annotated[str | None, Query(max_length=60)] = None,
    page: Annotated[int, Query(ge=1, le=1000)] = 1,
) -> FreeAgentPageOut:
    result = free_agent_service.search(ctx, user, sport, city, neighborhood, page)
    return FreeAgentPageOut.model_validate(asdict(result))


@router.post("/teams/{team_id}/invitations", status_code=201)
def invite(team_id: int, body: InviteRequest, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    invitation = invitation_service.invite(ctx, user, team_id, body.user_id, body.message)
    return {"id": invitation.id, "status": invitation.status}


@router.get("/me/invitations")
def my_invitations(ctx: CtxDep, user: UserDep) -> list[InvitationOut]:
    return [InvitationOut.model_validate(asdict(v)) for v in invitation_service.my_invitations(ctx, user)]


@router.post("/invitations/{invitation_id}/accept")
def accept_invitation(invitation_id: int, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    invitation = invitation_service.respond(ctx, user, invitation_id, accept=True)
    return {"id": invitation.id, "status": invitation.status}


@router.post("/invitations/{invitation_id}/reject")
def reject_invitation(invitation_id: int, ctx: CtxDep, user: UserDep) -> dict[str, object]:
    invitation = invitation_service.respond(ctx, user, invitation_id, accept=False)
    return {"id": invitation.id, "status": invitation.status}
