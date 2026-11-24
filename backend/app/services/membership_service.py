"""Cambios de plantilla: nombrar capitán y salir del equipo.

Ambos bloquean la fila del equipo para que dos cambios simultáneos se apliquen en serie,
y la base de datos garantiza un solo DT y un solo capitán (índices únicos parciales).
"""

from app.domain.errors import ConflictError, NotFoundError
from app.domain.roles import TeamRole
from app.domain.team_rules import check_can_leave, resolve_admin
from app.persistence.models_identity import UserAccount
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.team_service import get_active_team, member_views, record_admin_change, require_admin


def set_captain(ctx: ServiceContext, actor: UserAccount, team_id: int, new_captain_id: int) -> None:
    """Si quien administra es el capitán y nombra a otro, la administración pasa al nuevo capitán."""
    team = get_active_team(ctx, team_id, lock=True)
    require_admin(team, actor)
    target = next((m for m in team.memberships if m.user_id == new_captain_id), None)
    if target is None:
        raise NotFoundError("MEMBER_NOT_FOUND", "Esa persona no está en la plantilla.")
    if target.role == TeamRole.COACH:
        raise ConflictError("COACH_CANNOT_BE_CAPTAIN", "El DT no puede ser también el capitán.")
    if target.role == TeamRole.CAPTAIN:
        return
    admin_before = resolve_admin(member_views(team))
    previous = next((m for m in team.memberships if m.role == TeamRole.CAPTAIN), None)
    if previous is not None:
        previous.role = TeamRole.PLAYER.value
        ctx.db.flush()  # primero se libera el puesto de capitán para no chocar con el índice único
    target.role = TeamRole.CAPTAIN.value
    ctx.db.flush()
    record_event(
        ctx, action="CAPTAIN_SET", entity="team", entity_id=team.id, initiated_by=actor.id,
        before={"captain": previous.user_id if previous else None},
        after={"captain": new_captain_id},
    )
    record_admin_change(ctx, team, admin_before, actor.id)


def leave_team(ctx: ServiceContext, actor: UserAccount, team_id: int) -> None:
    team = get_active_team(ctx, team_id, lock=True)
    views = member_views(team)
    check_can_leave(actor.id, views)
    admin_before = resolve_admin(views)
    membership = next(m for m in team.memberships if m.user_id == actor.id)
    team.memberships.remove(membership)
    if not team.memberships:
        team.status = "ARCHIVED"
    ctx.db.flush()
    record_event(
        ctx, action="MEMBER_LEFT", entity="team", entity_id=team.id, initiated_by=actor.id,
        before={"role": membership.role}, after={"status": team.status},
    )
    record_admin_change(ctx, team, admin_before, actor.id)
