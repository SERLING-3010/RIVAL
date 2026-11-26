"""Pendientes de retos y ofertas (Sprint 25), para el administrador del equipo.

- Te retaron: una búsqueda abierta dirigida a tu equipo, vigente y sin oferta tuya pendiente.
- Ofertas para tu búsqueda: ofertas pendientes en una búsqueda abierta de tu equipo.
Devuelven tuplas (tipo, título, detalle, destino, id, hora), como `pending_sources`.
"""

from sqlalchemy import func, select

from app.domain.match_rules import OfferStatus, RequestStatus
from app.persistence.models_matches import MatchOffer, MatchRequest
from app.persistence.models_teams import Team
from app.services.context import ServiceContext
from app.services.pending_sources import Row


def challenges(ctx: ServiceContext, admin_teams: list[Team]) -> list[Row]:
    ids, now, rows = [t.id for t in admin_teams], ctx.clock.now(), []
    if not ids:
        return rows
    open_challenges = ctx.db.execute(
        select(MatchRequest, Team).join(Team, Team.id == MatchRequest.team_id)
        .where(MatchRequest.target_team_id.in_(ids), MatchRequest.status == RequestStatus.OPEN,
               MatchRequest.window_end > now)
        .order_by(MatchRequest.id)).all()
    for request, challenger in open_challenges:
        answered = ctx.db.scalar(select(MatchOffer.id).where(
            MatchOffer.request_id == request.id, MatchOffer.team_id == request.target_team_id,
            MatchOffer.status == OfferStatus.PENDING).limit(1))
        if answered is None:
            rows.append(("CHALLENGE_RECEIVED", f"Te retaron: {challenger.name}",
                         "Responde con una oferta desde las búsquedas de tu equipo.", "feed",
                         request.target_team_id, request.window_start))
    return rows


def offers(ctx: ServiceContext, admin_teams: list[Team]) -> list[Row]:
    ids, now = [t.id for t in admin_teams], ctx.clock.now()
    if not ids:
        return []
    counts = ctx.db.execute(
        select(MatchRequest, func.count(MatchOffer.id)).join(MatchOffer, MatchOffer.request_id == MatchRequest.id)
        .where(MatchRequest.team_id.in_(ids), MatchRequest.status == RequestStatus.OPEN,
               MatchRequest.window_end > now, MatchOffer.status == OfferStatus.PENDING)
        .group_by(MatchRequest.id).order_by(MatchRequest.id)).all()
    return [("OFFERS_RECEIVED", f"Ofertas para tu búsqueda ({n})", "Acepta una o recházalas.", "offers",
             request.id, request.window_start) for request, n in counts]
