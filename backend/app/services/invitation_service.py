"""Invitaciones de un equipo a un agente libre. El jugador siempre decide si entra."""

from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.domain.errors import ConflictError, NotFoundError
from app.domain.roles import TeamRole
from app.persistence.models_identity import UserAccount
from app.persistence.models_scouting import FreeAgentProfile
from app.persistence.models_teams import JoinRequest, Team, TeamMembership
from app.services import free_agent_service
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.team_service import get_active_team, require_admin, summary
from app.services.team_views import TeamSummaryView

_PENDING = "PENDING"
MAX_PENDING_INVITATIONS = 20
REINVITE_COOLDOWN = timedelta(days=7)
_ALREADY = "Ya hay una invitación o solicitud pendiente entre este equipo y esa persona."


@dataclass(frozen=True)
class InvitationView:
    id: int
    team: TeamSummaryView
    message: str | None


def invite(ctx: ServiceContext, actor: UserAccount, team_id: int, user_id: int, message: str | None) -> JoinRequest:
    team = get_active_team(ctx, team_id)
    require_admin(team, actor)
    if any(m.user_id == user_id for m in team.memberships):
        raise ConflictError("ALREADY_MEMBER", "Esa persona ya está en tu equipo.")
    free_agent = ctx.db.scalar(select(FreeAgentProfile.id).where(
        FreeAgentProfile.user_id == user_id, FreeAgentProfile.sport_code == team.sport_code,
        FreeAgentProfile.active.is_(True)))
    if free_agent is None:
        raise ConflictError("NOT_A_FREE_AGENT", "Solo puedes invitar a agentes libres de este deporte.")
    pending = ctx.db.scalar(select(JoinRequest.id).where(
        JoinRequest.team_id == team.id, JoinRequest.user_id == user_id, JoinRequest.status == _PENDING))
    if pending:
        raise ConflictError("INVITATION_ALREADY_PENDING", _ALREADY)
    _check_invitation_limits(ctx, team.id, user_id)
    invitation = JoinRequest(
        team_id=team.id, user_id=user_id, desired_role=TeamRole.PLAYER.value, direction="INVITE",
        initiated_by=actor.id, message=(message or "").strip()[:200] or None, status=_PENDING,
        created_at=ctx.clock.now(),
    )
    ctx.db.add(invitation)
    try:
        ctx.db.flush()
    except IntegrityError as error:
        raise ConflictError("INVITATION_ALREADY_PENDING", _ALREADY) from error
    record_event(ctx, action="PLAYER_INVITED", entity="join_request", entity_id=invitation.id,
                 initiated_by=actor.id, after={"team_id": team.id, "user_id": user_id})
    return invitation


def _check_invitation_limits(ctx: ServiceContext, team_id: int, user_id: int) -> None:
    """Evita el acoso: tope de invitaciones pendientes y una semana de espera tras un rechazo."""
    open_count = ctx.db.scalar(select(func.count()).select_from(JoinRequest).where(
        JoinRequest.team_id == team_id, JoinRequest.direction == "INVITE", JoinRequest.status == _PENDING)) or 0
    if open_count >= MAX_PENDING_INVITATIONS:
        raise ConflictError("TOO_MANY_INVITATIONS", "Tu equipo tiene 20 invitaciones sin responder. Espera respuestas.")
    recent_rejection = ctx.db.scalar(select(JoinRequest.id).where(
        JoinRequest.team_id == team_id, JoinRequest.user_id == user_id, JoinRequest.direction == "INVITE",
        JoinRequest.status == "REJECTED", JoinRequest.decided_at > ctx.clock.now() - REINVITE_COOLDOWN))
    if recent_rejection:
        raise ConflictError("INVITATION_COOLDOWN", "Esta persona rechazó tu invitación hace poco. Espera 7 días.")


def my_invitations(ctx: ServiceContext, actor: UserAccount) -> list[InvitationView]:
    rows = ctx.db.execute(
        select(JoinRequest, Team).join(Team, Team.id == JoinRequest.team_id).where(
            JoinRequest.user_id == actor.id, JoinRequest.direction == "INVITE",
            JoinRequest.status == _PENDING, Team.status == "ACTIVE").order_by(JoinRequest.id)
    ).all()
    return [InvitationView(id=r.id, team=summary(t), message=r.message) for r, t in rows]


def respond(ctx: ServiceContext, actor: UserAccount, invitation_id: int, accept: bool) -> JoinRequest:
    invitation = ctx.db.get(JoinRequest, invitation_id)
    # A quien no es el invitado se le responde igual que si no existiera.
    if invitation is None or invitation.direction != "INVITE" or invitation.user_id != actor.id:
        raise NotFoundError("INVITATION_NOT_FOUND", "La invitación no existe.")
    team = get_active_team(ctx, invitation.team_id, lock=True)
    ctx.db.refresh(invitation)  # un doble toque pudo responderla mientras esperábamos el bloqueo
    if invitation.status != _PENDING:
        raise ConflictError("INVITATION_ALREADY_DECIDED", "Esta invitación ya fue respondida.")
    now = ctx.clock.now()
    invitation.status = "APPROVED" if accept else "REJECTED"
    invitation.decided_by, invitation.decided_at = actor.id, now
    if accept:
        team.memberships.append(TeamMembership(user_id=actor.id, role=TeamRole.PLAYER.value, joined_at=now))
        free_agent_service.deactivate(ctx, actor.id, team.sport_code)
    ctx.db.flush()
    record_event(ctx, action="INVITATION_ACCEPTED" if accept else "INVITATION_REJECTED", entity="join_request",
                 entity_id=invitation.id, initiated_by=invitation.initiated_by, approved_by=actor.id,
                 before={"status": _PENDING}, after={"status": invitation.status})
    return invitation
