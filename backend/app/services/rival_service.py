"""Buscar rivales del mismo deporte y modalidad por cercanía, barrio o ciudad (ADR-006).

Solo se devuelve el barrio, la ciudad y un rango de distancia; nunca coordenadas.
"""

from dataclasses import dataclass

from sqlalchemy import func, select

from app.domain.errors import DomainError, PermissionDeniedError
from app.domain.geo import DEFAULT_RADIUS_KM, DistanceBand, SearchScope, distance_band, validate_radius_km
from app.persistence.models_identity import UserAccount
from app.persistence.models_teams import Team
from app.services import neighborhood_service
from app.services import block_service, settlement_service
from app.services.context import ServiceContext
from app.services.team_service import MAX_PAGE_SIZE, get_active_team, summary
from app.services.team_views import TeamSummaryView


RELIABLE_RD = 100.0  # [SUPUESTO] por debajo de esto el nivel se muestra como confiable


@dataclass(frozen=True)
class RivalView:
    team: TeamSummaryView
    distance_band: DistanceBand | None
    level: int | None  # nivel Glicko-2 redondeado (Sprint 10); None si aún no juega partidos confirmados
    level_reliable: bool  # RD baja: el nivel ya es confiable


@dataclass(frozen=True)
class RivalPage:
    items: list[RivalView]
    page: int
    page_size: int
    total: int


def require_member(team: Team, actor: UserAccount) -> None:
    if not any(m.user_id == actor.id for m in team.memberships):
        raise PermissionDeniedError("MEMBERS_ONLY", "Solo los miembros del equipo pueden buscar en su nombre.")


def nearby_keys(ctx: ServiceContext, team: Team, radius_km: int) -> dict[str, float]:
    keys = neighborhood_service.neighborhoods_within(ctx, team.city, team.neighborhood, validate_radius_km(radius_km))
    if not keys:
        raise DomainError(
            "NEIGHBORHOOD_NOT_IN_CATALOG",
            "Tu barrio aún no tiene ubicación en el catálogo. Busca por barrio o por ciudad.",
        )
    return keys


def search_rivals(
    ctx: ServiceContext,
    actor: UserAccount,
    team_id: int,
    scope: SearchScope,
    radius_km: int = DEFAULT_RADIUS_KM,
    page: int = 1,
    page_size: int = 20,
    by_level: bool = False,
) -> RivalPage:
    team = get_active_team(ctx, team_id)
    require_member(team, actor)
    page, page_size = max(1, page), max(1, min(page_size, MAX_PAGE_SIZE))
    stmt = select(Team).where(
        Team.status == "ACTIVE", Team.id != team.id, Team.sport_code == team.sport_code,
        Team.modality_code == team.modality_code, Team.city_key == team.city_key,
        Team.id.not_in(block_service.blocked_ids(ctx, team.id)),  # bloqueos entre equipos (Sprint 12)
    )
    distances: dict[str, float] = {}
    if scope == SearchScope.NEIGHBORHOOD:
        stmt = stmt.where(Team.neighborhood_key == team.neighborhood_key)
    elif scope == SearchScope.NEARBY:
        distances = nearby_keys(ctx, team, radius_km)
        stmt = stmt.where(Team.neighborhood_key.in_(list(distances)))
    total = ctx.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = list(ctx.db.scalars(stmt.order_by(Team.name_key, Team.id)))
    if scope == SearchScope.NEARBY:
        rows.sort(key=lambda t: (distances[t.neighborhood_key], t.name_key))  # el más cercano primero
    levels = settlement_service.ratings_for(ctx, [t.id for t in rows] + [team.id])
    if by_level:  # nivel parecido primero; sin nivel, al final (Sprint 11)
        mine = levels[team.id].rating if team.id in levels else 1500.0
        rows.sort(key=lambda t: (t.id not in levels, abs(levels[t.id].rating - mine) if t.id in levels else 0.0))
    chosen = rows[(page - 1) * page_size: page * page_size]
    items = [
        RivalView(team=summary(t), distance_band=distance_band(distances[t.neighborhood_key]) if distances else None,
                  level=round(levels[t.id].rating) if t.id in levels else None,
                  level_reliable=t.id in levels and levels[t.id].rd <= RELIABLE_RD)
        for t in chosen
    ]
    return RivalPage(items=items, page=page, page_size=page_size, total=total)
