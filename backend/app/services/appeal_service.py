"""Apelaciones de sanciones (Sprint 12): una por sanción, decidida por otro moderador (cuatro ojos)."""

from sqlalchemy import select

from app.domain.errors import ConflictError, NotFoundError
from app.domain.moderation_rules import check_appeal_window, check_four_eyes, validate_text
from app.persistence.models_identity import UserAccount
from app.persistence.models_moderation import Sanction
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.sanction_service import require_moderator


def appeal(ctx: ServiceContext, actor: UserAccount, sanction_id: int, text: str) -> Sanction:
    item = ctx.db.get(Sanction, sanction_id, with_for_update=True)
    if item is None or item.user_id != actor.id:
        raise NotFoundError("SANCTION_NOT_FOUND", "La sanción no existe.")
    if item.appealed_at is not None or item.status != "ACTIVE":
        raise ConflictError("ALREADY_APPEALED", "Esta sanción ya fue apelada o revocada.")
    check_appeal_window(item.created_at, ctx.clock.now())
    item.appeal_text, item.appealed_at = validate_text(text, 10, 500, "La apelación"), ctx.clock.now()
    ctx.db.flush()
    record_event(ctx, action="SANCTION_APPEALED", entity="sanction", entity_id=item.id, initiated_by=actor.id)
    return item


def appeals_queue(ctx: ServiceContext, actor: UserAccount) -> list[Sanction]:
    require_moderator(ctx, actor)
    return [s for s in ctx.db.scalars(select(Sanction).where(
        Sanction.appealed_at.is_not(None), Sanction.appeal_outcome.is_(None)).order_by(Sanction.appealed_at))
        if s.decided_by != actor.id and s.user_id != actor.id]


def decide_appeal(ctx: ServiceContext, actor: UserAccount, sanction_id: int, revoke: bool) -> Sanction:
    require_moderator(ctx, actor)
    item = ctx.db.get(Sanction, sanction_id, with_for_update=True)
    if item is None or item.appealed_at is None or item.appeal_outcome is not None:
        raise NotFoundError("APPEAL_NOT_FOUND", "No hay una apelación pendiente para esta sanción.")
    check_four_eyes(item.decided_by, actor.id)
    item.appeal_outcome = "REVOKED" if revoke else "UPHELD"
    item.appeal_decided_by, item.appeal_decided_at = actor.id, ctx.clock.now()
    if revoke:
        item.status = "REVOKED"
    ctx.db.flush()
    record_event(ctx, action="APPEAL_DECIDED", entity="sanction", entity_id=item.id, initiated_by=item.user_id,
                 approved_by=actor.id, after={"outcome": item.appeal_outcome})
    return item
