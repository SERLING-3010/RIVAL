"""Solicitudes para unirse a un equipo: pedir, listar (administrador) y decidir."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.domain.errors import ConflictError, NotFoundError, PermissionDeniedError
from app.domain.roles import TeamRole, UserRole
from app.persistence.models_identity import UserAccount
from app.persistence.models_teams import JoinRequest, TeamMembership
from app.services import free_agent_service
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.inputs import JoinRequestInput
from app.domain.team_rules import resolve_admin
from app.services.team_service import get_active_team, member_views, record_admin_change, require_admin
from app.services.team_views import JoinRequestView

_PENDING = "PENDING"


def request_join(ctx: ServiceContext, actor: UserAccount, team_id: int, data: JoinRequestInput) -> JoinRequest:
    team = get_active_team(ctx, team_id)
    if any(m.user_id == actor.id for m in team.memberships):
        raise ConflictError("ALREADY_MEMBER", "Ya eres parte de este equipo.")
    account_roles = {r.role for r in actor.roles}
    if not account_roles & {UserRole.PLAYER.value, UserRole.COACH.value}:
        raise PermissionDeniedError(
            "ROLE_CANNOT_JOIN_TEAM", "Agrega el rol de jugador o DT a tu cuenta para unirte a un equipo."
        )
    if data.desired_role == TeamRole.CAPTAIN:
        raise PermissionDeniedError("INVALID_DESIRED_ROLE", "El capitán lo nombra el administrador del equipo.")
    if data.desired_role == TeamRole.COACH and UserRole.COACH.value not in account_roles:
        raise PermissionDeniedError("COACH_ROLE_REQUIRED", "Para entrar como DT agrega el rol de director técnico.")
    existing = ctx.db.scalar(select(JoinRequest.id).where(
        JoinRequest.team_id == team.id, JoinRequest.user_id == actor.id, JoinRequest.status == _PENDING))
    if existing:
        raise ConflictError("REQUEST_ALREADY_PENDING", "Ya enviaste una solicitud; espera la respuesta del equipo.")
    request = JoinRequest(
        team_id=team.id, user_id=actor.id, desired_role=data.desired_role.value, initiated_by=actor.id,
        message=(data.message or "").strip()[:200] or None, status=_PENDING, created_at=ctx.clock.now(),
    )
    ctx.db.add(request)
    try:
        ctx.db.flush()
    except IntegrityError as error:
        raise ConflictError("REQUEST_ALREADY_PENDING", "Ya enviaste una solicitud; espera la respuesta del equipo.") from error
    record_event(ctx, action="JOIN_REQUESTED", entity="join_request", entity_id=request.id,
                 initiated_by=actor.id, after={"team_id": team.id, "desired_role": request.desired_role})
    return request


def list_requests(ctx: ServiceContext, actor: UserAccount, team_id: int) -> list[JoinRequestView]:
    team = get_active_team(ctx, team_id)
    require_admin(team, actor)
    rows = ctx.db.execute(
        select(JoinRequest, UserAccount).join(UserAccount, UserAccount.id == JoinRequest.user_id)
        .where(JoinRequest.team_id == team.id, JoinRequest.status == _PENDING, JoinRequest.direction == "REQUEST")
        .order_by(JoinRequest.id)
    ).all()
    return [
        JoinRequestView(id=r.id, team_id=r.team_id, user_id=r.user_id, display_name=u.display_name,
                        position=u.position, desired_role=TeamRole(r.desired_role), message=r.message,
                        status=r.status)
        for r, u in rows
    ]


def decide(ctx: ServiceContext, actor: UserAccount, request_id: int, approve: bool) -> JoinRequest:
    request = ctx.db.get(JoinRequest, request_id)
    if request is None or request.direction != "REQUEST":
        raise NotFoundError("REQUEST_NOT_FOUND", "La solicitud no existe.")
    team = get_active_team(ctx, request.team_id, lock=True)
    require_admin(team, actor)
    ctx.db.refresh(request)  # otra petición pudo decidirla mientras esperábamos el bloqueo
    if request.status != _PENDING:
        raise ConflictError("REQUEST_ALREADY_DECIDED", "Esta solicitud ya fue respondida.")
    if approve and request.desired_role == TeamRole.COACH and any(m.role == TeamRole.COACH for m in team.memberships):
        raise ConflictError("TEAM_HAS_COACH", "El equipo ya tiene DT. Acepta a la persona como jugador o rechaza.")
    admin_before = resolve_admin(member_views(team))
    now = ctx.clock.now()
    request.status = "APPROVED" if approve else "REJECTED"
    request.decided_by = actor.id
    request.decided_at = now
    if approve:
        team.memberships.append(TeamMembership(user_id=request.user_id, role=request.desired_role, joined_at=now))
        free_agent_service.deactivate(ctx, request.user_id, team.sport_code)
    ctx.db.flush()
    record_event(ctx, action="JOIN_APPROVED" if approve else "JOIN_REJECTED", entity="join_request",
                 entity_id=request.id, initiated_by=request.user_id, approved_by=actor.id,
                 before={"status": _PENDING}, after={"status": request.status, "role": request.desired_role})
    record_admin_change(ctx, team, admin_before, actor.id)
    return request
