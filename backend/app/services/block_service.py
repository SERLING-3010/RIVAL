"""Bloqueo entre equipos (Sprint 12): mientras dure, ninguno ve al otro ni puede retarlo u ofertarle."""

from dataclasses import dataclass

from sqlalchemy import delete, or_, select

from app.domain.errors import ConflictError
from app.persistence.models_identity import UserAccount
from app.persistence.models_moderation import TeamBlock
from app.persistence.models_teams import Team
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.team_service import get_active_team, require_admin, summary
from app.services.team_views import TeamSummaryView


@dataclass(frozen=True)
class BlockedView:
    team: TeamSummaryView


def blocked_ids(ctx: ServiceContext, team_id: int) -> set[int]:
    """Equipos bloqueados en cualquier dirección: los que bloqueé y los que me bloquearon."""
    rows = ctx.db.execute(select(TeamBlock.blocker_team_id, TeamBlock.blocked_team_id).where(
        or_(TeamBlock.blocker_team_id == team_id, TeamBlock.blocked_team_id == team_id))).all()
    return {b if a == team_id else a for a, b in rows}


def is_blocked(ctx: ServiceContext, team_a: int, team_b: int) -> bool:
    return team_b in blocked_ids(ctx, team_a)


def block(ctx: ServiceContext, actor: UserAccount, team_id: int, other_id: int) -> None:
    team = get_active_team(ctx, team_id, lock=True)
    require_admin(team, actor)
    get_active_team(ctx, other_id)
    if other_id == team.id:
        raise ConflictError("CANNOT_BLOCK_SELF", "No puedes bloquear a tu propio equipo.")
    if ctx.db.scalar(select(TeamBlock.id).where(TeamBlock.blocker_team_id == team.id,
                                                TeamBlock.blocked_team_id == other_id)) is not None:
        raise ConflictError("ALREADY_BLOCKED", "Ya bloqueaste a ese equipo.")
    ctx.db.add(TeamBlock(blocker_team_id=team.id, blocked_team_id=other_id, created_by=actor.id,
                         created_at=ctx.clock.now()))
    ctx.db.flush()
    record_event(ctx, action="TEAM_BLOCKED", entity="team", entity_id=team.id, initiated_by=actor.id,
                 after={"blocked_team_id": other_id})


def unblock(ctx: ServiceContext, actor: UserAccount, team_id: int, other_id: int) -> None:
    team = get_active_team(ctx, team_id, lock=True)
    require_admin(team, actor)
    ctx.db.execute(delete(TeamBlock).where(TeamBlock.blocker_team_id == team.id, TeamBlock.blocked_team_id == other_id))
    record_event(ctx, action="TEAM_UNBLOCKED", entity="team", entity_id=team.id, initiated_by=actor.id,
                 after={"blocked_team_id": other_id})


def blocked_by(ctx: ServiceContext, actor: UserAccount, team_id: int) -> list[BlockedView]:
    team = get_active_team(ctx, team_id)
    require_admin(team, actor)
    rows = ctx.db.scalars(select(Team).join(TeamBlock, TeamBlock.blocked_team_id == Team.id)
                          .where(TeamBlock.blocker_team_id == team.id).order_by(Team.name_key))
    return [BlockedView(team=summary(t)) for t in rows]
