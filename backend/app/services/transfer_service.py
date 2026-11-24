"""Mercado de fichajes con monedas RIVAL (Sprint 7, RIV-015).

Orden: el comprador ofrece → el administrador del equipo dueño acepta → el jugador acepta.
Solo con las dos aceptaciones se mueven el jugador y las monedas, en una sola transacción y con
los dos equipos bloqueados en orden de id (así dos traspasos cruzados no se bloquean entre sí).
"""

from sqlalchemy import delete, select

from app.domain.errors import ConflictError, NotFoundError, PermissionDeniedError
from app.domain.manager_rules import ACTIVE_TRANSFERS, check_balance, validate_offer_amount
from app.domain.manager_rules import TransferStatus as TS
from app.domain.roles import TeamRole
from app.persistence.models_identity import UserAccount
from app.persistence.models_manager import TransferListing, TransferOffer
from app.persistence.models_teams import TeamMembership
from app.services import coin_service
from app.services.audit_service import record_event
from app.services.transfer_listing_service import close_others as _close_others
from app.services.transfer_listing_service import listing as _listing
from app.services.context import ServiceContext
from app.services.team_service import get_active_team, require_admin


def make_offer(ctx: ServiceContext, actor: UserAccount, buyer_team_id: int, player_id: int,
               amount: int) -> TransferOffer:
    buyer = get_active_team(ctx, buyer_team_id, lock=True)
    require_admin(buyer, actor)
    validate_offer_amount(amount)
    listing = _listing(ctx, player_id)
    if listing is None:
        raise ConflictError("NOT_LISTED", "Ese jugador no está en el mercado de fichajes.")
    seller = get_active_team(ctx, listing.team_id)
    if seller.id == buyer.id or any(m.user_id == player_id for m in buyer.memberships):
        raise ConflictError("ALREADY_IN_TEAM", "Ese jugador ya está en tu equipo.")
    if seller.sport_code != buyer.sport_code:
        raise ConflictError("TEAM_SPORT_MISMATCH", "Solo puedes fichar jugadores de equipos de tu mismo deporte.")
    check_balance(coin_service.balance(ctx, buyer.id), amount)
    for previous in ctx.db.scalars(select(TransferOffer).where(
            TransferOffer.player_id == player_id, TransferOffer.to_team_id == buyer.id,
            TransferOffer.status.in_(ACTIVE_TRANSFERS))):
        previous.status, previous.closed_at = TS.WITHDRAWN.value, ctx.clock.now()
    ctx.db.flush()  # libera el índice de oferta activa antes de crear la nueva
    offer = TransferOffer(player_id=player_id, from_team_id=seller.id, to_team_id=buyer.id, amount=amount,
                          status=TS.PENDING_OWNER.value, offered_by=actor.id, created_at=ctx.clock.now())
    ctx.db.add(offer)
    ctx.db.flush()
    record_event(ctx, action="TRANSFER_OFFERED", entity="transfer_offer", entity_id=offer.id, initiated_by=actor.id,
                 after={"player_id": player_id, "from": seller.id, "to": buyer.id, "amount": amount})
    return offer


def _offer(ctx: ServiceContext, offer_id: int) -> TransferOffer:
    offer = ctx.db.get(TransferOffer, offer_id, with_for_update=True)
    if offer is None:
        raise NotFoundError("TRANSFER_OFFER_NOT_FOUND", "La oferta de traspaso no existe.")
    return offer


def _record(ctx: ServiceContext, offer: TransferOffer, action: str, actor_id: int, before: str) -> None:
    record_event(ctx, action=action, entity="transfer_offer", entity_id=offer.id, initiated_by=offer.offered_by,
                 approved_by=actor_id, before={"status": before}, after={"status": offer.status})


def decide_owner(ctx: ServiceContext, actor: UserAccount, offer_id: int, accept: bool) -> TransferOffer:
    offer = _offer(ctx, offer_id)
    require_admin(get_active_team(ctx, offer.from_team_id), actor)
    if offer.status != TS.PENDING_OWNER:
        raise ConflictError("OFFER_NOT_PENDING", "Esta oferta ya no espera tu decisión.")
    offer.status = (TS.PENDING_PLAYER if accept else TS.REJECTED).value
    offer.owner_decided_by, offer.owner_decided_at = actor.id, ctx.clock.now()
    offer.closed_at = None if accept else ctx.clock.now()
    ctx.db.flush()
    _record(ctx, offer, "TRANSFER_OWNER_ACCEPTED" if accept else "TRANSFER_OWNER_REJECTED", actor.id,
            TS.PENDING_OWNER.value)
    return offer


def decide_player(ctx: ServiceContext, actor: UserAccount, offer_id: int, accept: bool) -> TransferOffer:
    """Solo el jugador decide sobre su propio traspaso, y solo después de que su DT aceptó."""
    offer = _offer(ctx, offer_id)
    if actor.id != offer.player_id:
        raise PermissionDeniedError("PLAYER_ONLY", "Solo el jugador puede aceptar o rechazar su traspaso.")
    if offer.status == TS.PENDING_OWNER:
        raise PermissionDeniedError("OWNER_FIRST", "Primero debe decidir el administrador de tu equipo.")
    if offer.status != TS.PENDING_PLAYER:
        raise ConflictError("OFFER_NOT_PENDING", "Esta oferta ya no está pendiente.")
    offer.player_decided_at = ctx.clock.now()
    if not accept:
        offer.status, offer.closed_at = TS.REJECTED.value, ctx.clock.now()
        ctx.db.flush()
        _record(ctx, offer, "TRANSFER_PLAYER_REJECTED", actor.id, TS.PENDING_PLAYER.value)
        return offer
    _complete(ctx, offer, actor)
    return offer


def _complete(ctx: ServiceContext, offer: TransferOffer, player: UserAccount) -> None:
    first, second = sorted((offer.from_team_id, offer.to_team_id))
    teams = {t: get_active_team(ctx, t, lock=True) for t in (first, second)}
    seller, buyer = teams[offer.from_team_id], teams[offer.to_team_id]
    member = next((m for m in seller.memberships if m.user_id == player.id), None)
    if member is None or member.role != TeamRole.PLAYER or _listing(ctx, player.id) is None:
        raise ConflictError("TRANSFER_NO_LONGER_VALID", "Este traspaso ya no es posible: cambió la plantilla.")
    reference = f"transfer:{offer.id}"
    coin_service.move(ctx, buyer.id, -offer.amount, "TRANSFER_PAID", reference, player.id)
    coin_service.move(ctx, seller.id, offer.amount, "TRANSFER_RECEIVED", reference, player.id)
    seller.memberships.remove(member)
    ctx.db.flush()
    buyer.memberships.append(TeamMembership(user_id=player.id, role=TeamRole.PLAYER.value, joined_at=ctx.clock.now()))
    ctx.db.execute(delete(TransferListing).where(TransferListing.user_id == player.id))
    offer.status, offer.closed_at = TS.COMPLETED.value, ctx.clock.now()
    _close_others(ctx, player.id, offer.id, TS.CANCELLED.value)
    ctx.db.flush()
    _record(ctx, offer, "TRANSFER_COMPLETED", player.id, TS.PENDING_PLAYER.value)


def withdraw(ctx: ServiceContext, actor: UserAccount, offer_id: int) -> TransferOffer:
    offer = _offer(ctx, offer_id)
    require_admin(get_active_team(ctx, offer.to_team_id), actor)
    if offer.status not in ACTIVE_TRANSFERS:
        raise ConflictError("OFFER_NOT_PENDING", "Esta oferta ya está cerrada.")
    before = offer.status
    offer.status, offer.closed_at = TS.WITHDRAWN.value, ctx.clock.now()
    ctx.db.flush()
    _record(ctx, offer, "TRANSFER_WITHDRAWN", actor.id, before)
    return offer

