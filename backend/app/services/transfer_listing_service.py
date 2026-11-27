"""Jugadores transferibles: el administrador los pone o los quita del mercado (Sprint 7, RIV-015)."""

from sqlalchemy import select

from app.domain.errors import NotFoundError
from app.domain.manager_rules import ACTIVE_TRANSFERS, check_transferable
from app.domain.manager_rules import TransferStatus as TS
from app.domain.roles import TeamRole
from app.persistence.models_identity import UserAccount
from app.persistence.models_manager import TransferListing, TransferOffer
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.team_service import get_active_team, require_admin


def listing(ctx: ServiceContext, user_id: int) -> TransferListing | None:
    return ctx.db.scalar(select(TransferListing).where(TransferListing.user_id == user_id))


def close_others(ctx: ServiceContext, player_id: int, keep_id: int | None, status: str) -> None:
    """Cierra las ofertas activas por el jugador, salvo la que se conserva."""
    for other in ctx.db.scalars(select(TransferOffer).where(
            TransferOffer.player_id == player_id, TransferOffer.status.in_(ACTIVE_TRANSFERS),
            TransferOffer.id != (keep_id or 0))):
        other.status, other.closed_at = status, ctx.clock.now()


def set_listed(ctx: ServiceContext, actor: UserAccount, team_id: int, user_id: int, listed: bool) -> None:
    team = get_active_team(ctx, team_id, lock=True)
    require_admin(team, actor)
    member = next((m for m in team.memberships if m.user_id == user_id), None)
    if member is None:
        raise NotFoundError("MEMBER_NOT_FOUND", "Esa persona no está en la plantilla.")
    current = listing(ctx, user_id)
    if listed and current is None:
        check_transferable(TeamRole(member.role))
        ctx.db.add(TransferListing(team_id=team.id, user_id=user_id, listed_by=actor.id, listed_at=ctx.clock.now()))
    elif not listed and current is not None:
        ctx.db.delete(current)
        close_others(ctx, user_id, None, TS.CANCELLED.value)
    else:
        return
    ctx.db.flush()
    record_event(ctx, action="TRANSFER_LISTED" if listed else "TRANSFER_UNLISTED", entity="team",
                 entity_id=team.id, initiated_by=actor.id, after={"user_id": user_id})
