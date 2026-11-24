"""Búsquedas de partido abiertas que un equipo puede responder.

Una solicitud se ve solo si el equipo que mira está dentro del alcance que pidió quien
la publicó (cercanía, barrio o ciudad) y dentro del alcance que eligió quien mira.
Los retos directos solo los ve el equipo retado. La misma regla protege las ofertas.
"""

from sqlalchemy import and_, func, or_, select

from app.domain.geo import DEFAULT_RADIUS_KM, MAX_RADIUS_KM, SearchScope, distance_band
from app.domain.match_rules import OfferStatus, RequestStatus
from app.persistence.models_identity import UserAccount
from app.persistence.models_matches import MatchOffer, MatchRequest
from app.persistence.models_teams import Team
from app.services import neighborhood_service
from app.services.context import ServiceContext
from app.services.match_request_service import to_view
from app.services.match_views import MatchRequestView
from app.services.rival_service import require_member
from app.services.team_service import get_active_team

MAX_RESULTS = 200


def _in_scope(scope: str, radius_km: int | None, same_barrio: bool, km: float | None) -> bool:
    if scope == SearchScope.CITY:
        return True
    if scope == SearchScope.NEIGHBORHOOD:
        return same_barrio
    return km is not None and km <= (radius_km or DEFAULT_RADIUS_KM)


def viewer_distances(ctx: ServiceContext, viewer: Team) -> dict[str, float]:
    """Distancia desde el barrio de quien mira a cada barrio de su ciudad dentro del radio máximo."""
    return neighborhood_service.neighborhoods_within(ctx, viewer.city, viewer.neighborhood, radius_km=MAX_RADIUS_KM)


def is_visible_to(request: MatchRequest, owner: Team, viewer: Team, distances: dict[str, float]) -> bool:
    """¿Puede `viewer` ver (y por tanto ofertar a) esta búsqueda?"""
    if owner.id == viewer.id or (request.sport_code, request.modality_code) != (viewer.sport_code, viewer.modality_code):
        return False
    if request.target_team_id is not None:
        return request.target_team_id == viewer.id
    if owner.city_key != viewer.city_key:
        return False
    same_barrio = owner.neighborhood_key == viewer.neighborhood_key
    return _in_scope(request.scope, request.radius_km, same_barrio, distances.get(owner.neighborhood_key))


def open_requests_for(
    ctx: ServiceContext, actor: UserAccount, team_id: int, scope: SearchScope, radius_km: int = DEFAULT_RADIUS_KM
) -> list[MatchRequestView]:
    viewer = get_active_team(ctx, team_id)
    require_member(viewer, actor)
    distances = viewer_distances(ctx, viewer)
    reachable = list(distances) or [viewer.neighborhood_key]
    rows = ctx.db.execute(
        select(MatchRequest, Team).join(Team, Team.id == MatchRequest.team_id).where(
            MatchRequest.status == RequestStatus.OPEN, MatchRequest.window_end > ctx.clock.now(),
            MatchRequest.team_id != viewer.id, MatchRequest.sport_code == viewer.sport_code,
            MatchRequest.modality_code == viewer.modality_code, Team.status == "ACTIVE",
            or_(
                MatchRequest.target_team_id == viewer.id,
                and_(MatchRequest.target_team_id.is_(None), Team.city_key == viewer.city_key,
                     or_(MatchRequest.scope == SearchScope.CITY.value, Team.neighborhood_key.in_(reachable))),
            ),
        ).order_by(MatchRequest.window_start, MatchRequest.id).limit(MAX_RESULTS * 2)
    ).all()
    visible = []
    for request, owner in rows:
        km = distances.get(owner.neighborhood_key)
        same_barrio = owner.neighborhood_key == viewer.neighborhood_key
        direct = request.target_team_id == viewer.id
        if is_visible_to(request, owner, viewer, distances) and (direct or _in_scope(scope, radius_km, same_barrio, km)):
            visible.append((request, km))
    visible = visible[:MAX_RESULTS]
    pending = dict(ctx.db.execute(
        select(MatchOffer.request_id, func.count()).where(
            MatchOffer.request_id.in_([r.id for r, _ in visible]), MatchOffer.status == OfferStatus.PENDING)
        .group_by(MatchOffer.request_id)).tuples().all())
    return [to_view(ctx, r, distance_band(km) if km is not None else None, pending.get(r.id, 0)) for r, km in visible]
