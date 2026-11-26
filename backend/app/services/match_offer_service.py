"""Ofertas de rivales a una búsqueda de partido, al estilo InDriver.

Una contraoferta del mismo equipo crea una versión nueva y deja la anterior SUPERSEDED. Aceptar crea el contrato del partido (Sprint 3).
Aceptar bloquea la solicitud (FOR UPDATE): dos aceptaciones simultáneas no pueden ganar ambas.
"""

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.domain import launch_rules
from app.domain.errors import ConflictError, NotFoundError
from app.domain.match_rules import (
    OfferStatus,
    RefereeMode,
    RequestStatus,
    check_offer_referee,
    check_proposed_start,
)
from app.persistence.models_identity import UserAccount
from app.persistence.models_matches import MatchOffer, MatchRequest
from app.persistence.models_teams import Team
from app.services import block_service, contract_service
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.match_feed_service import is_visible_to, viewer_distances
from app.services.match_request_service import effective_status, get_request
from app.services.match_views import OfferInput, OfferView
from app.services.team_service import get_active_team, require_admin, resolve_admin_id, summary

_PENDING = OfferStatus.PENDING.value


def _require_open(ctx: ServiceContext, request: MatchRequest) -> None:
    if effective_status(request, ctx) != RequestStatus.OPEN:
        raise ConflictError("MATCH_REQUEST_CLOSED", "Esta búsqueda ya está cerrada o venció.")


def make_offer(ctx: ServiceContext, actor: UserAccount, team_id: int, request_id: int, data: OfferInput) -> MatchOffer:
    team = get_active_team(ctx, team_id)
    require_admin(team, actor)
    request = get_request(ctx, request_id, lock=True)
    _require_open(ctx, request)
    if request.team_id == team.id:
        raise ConflictError("OWN_REQUEST", "No puedes ofertar a la búsqueda de tu propio equipo.")
    owner = ctx.db.get(Team, request.team_id)
    blocked = owner is not None and block_service.is_blocked(ctx, owner.id, team.id)
    if owner is None or blocked or not is_visible_to(request, owner, team, viewer_distances(ctx, team)):
        raise NotFoundError("MATCH_REQUEST_NOT_FOUND", "La búsqueda de partido no existe.")
    check_proposed_start(data.proposed_start, request.window_start, request.window_end, ctx.clock.now())
    check_offer_referee(RefereeMode(request.referee_mode), data.referee_mode)
    previous = ctx.db.scalar(select(MatchOffer).where(
        MatchOffer.request_id == request.id, MatchOffer.team_id == team.id, MatchOffer.status == _PENDING))
    if previous is not None:
        previous.status = OfferStatus.SUPERSEDED.value
        ctx.db.flush()  # libera el índice único de oferta pendiente antes de crear la nueva versión
    referee = launch_rules.match_terms(ctx.features, data.referee_mode, data.place_kind)  # Sprint 29
    offer = MatchOffer(
        request_id=request.id, team_id=team.id, version=_next_version(ctx, request.id, team.id),
        proposed_start=data.proposed_start, referee_mode=referee.value, place_kind=data.place_kind.value,
        place_note=(data.place_note or "").strip()[:120] or None, message=(data.message or "").strip()[:200] or None,
        status=_PENDING, created_by=actor.id, created_at=ctx.clock.now(),
    )
    ctx.db.add(offer)
    try:
        ctx.db.flush()
    except IntegrityError as error:
        raise ConflictError("OFFER_ALREADY_PENDING", "Ya hay una oferta pendiente de tu equipo.") from error
    record_event(ctx, action="MATCH_OFFER_MADE", entity="match_offer", entity_id=offer.id, initiated_by=actor.id,
                 after={"request_id": request.id, "team_id": team.id, "version": offer.version,
                        "proposed_start": offer.proposed_start.isoformat()})
    return offer


def _next_version(ctx: ServiceContext, request_id: int, team_id: int) -> int:
    last = ctx.db.scalar(select(func.max(MatchOffer.version)).where(
        MatchOffer.request_id == request_id, MatchOffer.team_id == team_id))
    return (last or 0) + 1


def _get_offer(ctx: ServiceContext, offer_id: int) -> MatchOffer:
    offer = ctx.db.get(MatchOffer, offer_id)
    if offer is None:
        raise NotFoundError("OFFER_NOT_FOUND", "La oferta no existe.")
    return offer


def decide(ctx: ServiceContext, actor: UserAccount, offer_id: int, accept: bool) -> MatchOffer:
    """El administrador del equipo que publicó la búsqueda acepta o rechaza una oferta."""
    offer = _get_offer(ctx, offer_id)
    request = get_request(ctx, offer.request_id, lock=True)
    require_admin(get_active_team(ctx, request.team_id), actor)
    ctx.db.refresh(offer)
    _require_open(ctx, request)
    if offer.status != _PENDING:
        raise ConflictError("OFFER_NOT_PENDING", "Esta oferta ya no está pendiente.")
    now = ctx.clock.now()
    if accept and offer.proposed_start < now:
        raise ConflictError("OFFER_IN_PAST", "La hora de esta oferta ya pasó. Pide una oferta nueva.")
    offer.status = (OfferStatus.ACCEPTED if accept else OfferStatus.REJECTED).value
    offer.decided_by, offer.decided_at = actor.id, now
    if accept:
        request.status, request.accepted_offer_id, request.closed_at = RequestStatus.MATCHED.value, offer.id, now
        for other in ctx.db.scalars(select(MatchOffer).where(
                MatchOffer.request_id == request.id, MatchOffer.status == _PENDING, MatchOffer.id != offer.id)):
            other.status, other.decided_by, other.decided_at = OfferStatus.SUPERSEDED.value, actor.id, now
    ctx.db.flush()
    offering_admin = resolve_admin_id(ctx, offer.team_id)
    record_event(ctx, action="MATCH_OFFER_ACCEPTED" if accept else "MATCH_OFFER_REJECTED", entity="match_offer",
                 entity_id=offer.id, initiated_by=offering_admin, approved_by=actor.id,
                 before={"status": _PENDING}, after={"status": offer.status, "request_status": request.status})
    if accept:  # después del evento de la oferta, para que la actividad se lea en orden
        contract_service.create_from_offer(ctx, request, offer, actor.id)
    return offer


def withdraw(ctx: ServiceContext, actor: UserAccount, offer_id: int) -> MatchOffer:
    offer = _get_offer(ctx, offer_id)
    require_admin(get_active_team(ctx, offer.team_id), actor)
    get_request(ctx, offer.request_id, lock=True)  # mismo orden de bloqueo que aceptar: no pueden cruzarse
    ctx.db.refresh(offer)
    if offer.status != _PENDING:
        raise ConflictError("OFFER_NOT_PENDING", "Esta oferta ya no está pendiente.")
    offer.status, offer.decided_by, offer.decided_at = OfferStatus.WITHDRAWN.value, actor.id, ctx.clock.now()
    ctx.db.flush()
    record_event(ctx, action="MATCH_OFFER_WITHDRAWN", entity="match_offer", entity_id=offer.id,
                 initiated_by=actor.id, before={"status": _PENDING}, after={"status": offer.status})
    return offer


def list_offers(ctx: ServiceContext, actor: UserAccount, request_id: int) -> list[OfferView]:
    """Los miembros del equipo que publicó ven todas; cualquier otro ve solo las de sus equipos."""
    request = get_request(ctx, request_id)
    owner = get_active_team(ctx, request.team_id)
    stmt = select(MatchOffer, Team).join(Team, Team.id == MatchOffer.team_id).where(MatchOffer.request_id == request.id)
    if not any(m.user_id == actor.id for m in owner.memberships):
        mine = [t.id for t in ctx.db.scalars(select(Team).where(Team.memberships.any(user_id=actor.id)))]
        stmt = stmt.where(MatchOffer.team_id.in_(mine))
    rows = ctx.db.execute(stmt.order_by(MatchOffer.id)).all()
    return [
        OfferView(id=o.id, request_id=o.request_id, team=summary(t), version=o.version,
                  proposed_start=o.proposed_start, referee_mode=o.referee_mode, place_kind=o.place_kind,
                  place_note=o.place_note, message=o.message, status=o.status)
        for o, t in rows
    ]
