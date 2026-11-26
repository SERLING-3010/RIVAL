"""Solicitudes de partido: abiertas (para equipos cercanos) o retos directos a un equipo."""

from sqlalchemy import func, select

from app.domain import launch_rules
from app.domain.errors import ConflictError, DomainError, NotFoundError
from app.domain.geo import DistanceBand, SearchScope, validate_radius_km
from app.domain.match_rules import MAX_OPEN_REQUESTS_PER_TEAM, OfferStatus, RequestStatus, validate_window
from app.persistence.models_identity import UserAccount
from app.persistence.models_matches import MatchOffer, MatchRequest
from app.persistence.models_teams import Team
from app.services import block_service
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.match_views import MatchRequestInput, MatchRequestView
from app.services.rival_service import nearby_keys, require_member
from app.services.team_service import get_active_team, require_admin, summary


def effective_status(request: MatchRequest, ctx: ServiceContext) -> str:
    if request.status == RequestStatus.OPEN and request.window_end <= ctx.clock.now():
        return "EXPIRED"
    return request.status


def to_view(
    ctx: ServiceContext, request: MatchRequest, band: DistanceBand | None = None, pending: int | None = None
) -> MatchRequestView:
    team = ctx.db.get(Team, request.team_id)
    assert team is not None
    if pending is None:
        pending = ctx.db.scalar(select(func.count()).select_from(MatchOffer).where(
            MatchOffer.request_id == request.id, MatchOffer.status == OfferStatus.PENDING)) or 0
    return MatchRequestView(
        id=request.id, team=summary(team), target_team_id=request.target_team_id, scope=request.scope,
        radius_km=request.radius_km, window_start=request.window_start, window_end=request.window_end,
        referee_mode=request.referee_mode, place_kind=request.place_kind, place_note=request.place_note,
        message=request.message, status=effective_status(request, ctx), distance_band=band,
        pending_offers=pending, accepted_offer_id=request.accepted_offer_id,
    )


def create_request(ctx: ServiceContext, actor: UserAccount, team_id: int, data: MatchRequestInput) -> MatchRequest:
    team = get_active_team(ctx, team_id, lock=True)
    require_admin(team, actor)
    now = ctx.clock.now()
    validate_window(data.window_start, data.window_end, now)
    open_count = ctx.db.scalar(select(func.count()).select_from(MatchRequest).where(
        MatchRequest.team_id == team.id, MatchRequest.status == RequestStatus.OPEN,
        MatchRequest.window_end > now)) or 0
    if open_count >= MAX_OPEN_REQUESTS_PER_TEAM:
        raise ConflictError("TOO_MANY_OPEN_REQUESTS", "Tu equipo ya tiene 3 búsquedas abiertas. Cierra una primero.")
    radius = None
    if data.scope == SearchScope.NEARBY:
        radius = validate_radius_km(data.radius_km or 0)
        nearby_keys(ctx, team, radius)  # falla con un mensaje claro si el barrio no está en el catálogo
    if data.target_team_id is not None:
        target = get_active_team(ctx, data.target_team_id)
        if block_service.is_blocked(ctx, team.id, target.id):
            raise NotFoundError("TEAM_NOT_FOUND", "El equipo no existe o ya no está activo.")
        same_game = (target.sport_code, target.modality_code, target.city_key) == (
            team.sport_code, team.modality_code, team.city_key)
        if target.id == team.id or not same_game:
            raise DomainError("INVALID_CHALLENGE", "Solo puedes retar a otro equipo de tu ciudad, deporte y modalidad.")
    referee = launch_rules.match_terms(ctx.features, data.referee_mode, data.place_kind)  # Sprint 29
    request = MatchRequest(
        team_id=team.id, target_team_id=data.target_team_id, sport_code=team.sport_code,
        modality_code=team.modality_code, scope=data.scope.value, radius_km=radius,
        window_start=data.window_start, window_end=data.window_end, referee_mode=referee.value,
        place_kind=data.place_kind.value, place_note=(data.place_note or "").strip()[:120] or None,
        message=(data.message or "").strip()[:200] or None, status=RequestStatus.OPEN.value,
        created_by=actor.id, created_at=now,
    )
    ctx.db.add(request)
    ctx.db.flush()
    record_event(ctx, action="MATCH_REQUEST_CREATED", entity="match_request", entity_id=request.id,
                 initiated_by=actor.id, after={"team_id": team.id, "target_team_id": data.target_team_id,
                                               "scope": request.scope, "referee_mode": request.referee_mode})
    return request


def get_request(ctx: ServiceContext, request_id: int, lock: bool = False) -> MatchRequest:
    request = ctx.db.get(MatchRequest, request_id, with_for_update=lock)
    if request is None:
        raise NotFoundError("MATCH_REQUEST_NOT_FOUND", "La búsqueda de partido no existe.")
    return request


def cancel_request(ctx: ServiceContext, actor: UserAccount, request_id: int) -> MatchRequest:
    request = get_request(ctx, request_id, lock=True)
    require_admin(get_active_team(ctx, request.team_id), actor)
    if request.status != RequestStatus.OPEN:
        raise ConflictError("MATCH_REQUEST_CLOSED", "Esta búsqueda ya está cerrada.")
    now = ctx.clock.now()
    request.status, request.closed_at = RequestStatus.CANCELLED.value, now
    for offer in ctx.db.scalars(select(MatchOffer).where(
            MatchOffer.request_id == request.id, MatchOffer.status == OfferStatus.PENDING)):
        offer.status, offer.decided_by, offer.decided_at = OfferStatus.CANCELLED.value, actor.id, now
    ctx.db.flush()
    record_event(ctx, action="MATCH_REQUEST_CANCELLED", entity="match_request", entity_id=request.id,
                 initiated_by=actor.id, before={"status": "OPEN"}, after={"status": request.status})
    return request


def team_requests(ctx: ServiceContext, actor: UserAccount, team_id: int) -> list[MatchRequestView]:
    team = get_active_team(ctx, team_id)
    require_member(team, actor)
    rows = ctx.db.scalars(select(MatchRequest).where(MatchRequest.team_id == team.id)
                          .order_by(MatchRequest.id.desc()).limit(50))
    return [to_view(ctx, r) for r in rows]
