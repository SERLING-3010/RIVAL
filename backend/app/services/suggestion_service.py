"""Rivales sugeridos con motivos (Sprint 18): mismo deporte, modalidad y ciudad, sin bloqueados.

Usa solo datos que el equipo ya ve: barrio (por rangos de distancia), nivel y días en que juega.
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import or_, select

from app.domain import suggestion_rules
from app.domain.contract_rules import ContractStatus
from app.domain.geo import MAX_RADIUS_KM, DistanceBand, distance_band
from app.persistence.models_contracts import MatchContract, MatchContractVersion
from app.persistence.models_identity import UserAccount
from app.persistence.models_teams import Team
from app.services import block_service, neighborhood_service, settlement_service
from app.services.context import ServiceContext
from app.services.contract_queries import terms_of
from app.services.rival_service import require_member
from app.services.team_service import get_active_team, summary
from app.services.team_views import TeamSummaryView

RECENT = timedelta(days=30)
HISTORY = 10  # últimos partidos firmados de cada equipo para saber qué días juega


@dataclass(frozen=True)
class SuggestionView:
    team: TeamSummaryView
    distance_band: DistanceBand | None
    level: int | None
    reasons: list[str]


def _signed_matches(ctx: ServiceContext, team_ids: list[int]) -> list[tuple[int, int, datetime]]:
    """(local, visitante, hora) de los partidos firmados y no cancelados de esos equipos."""
    rows = ctx.db.execute(select(MatchContract, MatchContractVersion)
                          .join(MatchContractVersion, MatchContractVersion.id == MatchContract.signed_version_id)
                          .where(or_(MatchContract.host_team_id.in_(team_ids),
                                     MatchContract.guest_team_id.in_(team_ids)),
                                 MatchContract.status != ContractStatus.CANCELLED)
                          .order_by(MatchContract.id.desc()))
    return [(c.host_team_id, c.guest_team_id, terms_of(v).kickoff_at) for c, v in rows]


def rivals_for(ctx: ServiceContext, actor: UserAccount, team_id: int) -> list[SuggestionView]:
    team = get_active_team(ctx, team_id)
    require_member(team, actor)
    blocked = block_service.blocked_ids(ctx, team.id)
    candidates = [t for t in ctx.db.scalars(select(Team).where(
        Team.status == "ACTIVE", Team.id != team.id, Team.sport_code == team.sport_code,
        Team.modality_code == team.modality_code, Team.city_key == team.city_key)) if t.id not in blocked]
    distances = neighborhood_service.neighborhoods_within(ctx, team.city, team.neighborhood, MAX_RADIUS_KM)
    levels = settlement_service.ratings_for(ctx, [t.id for t in candidates] + [team.id])
    days: dict[int, list[datetime]] = defaultdict(list)
    recent: set[int] = set()
    now = ctx.clock.now()
    for host, guest, kickoff in _signed_matches(ctx, [t.id for t in candidates] + [team.id]):
        for side in (host, guest):
            if len(days[side]) < HISTORY:
                days[side].append(kickoff)
        if team.id in (host, guest) and kickoff >= now - RECENT:  # recientes o ya pactados
            recent.add(guest if host == team.id else host)
    mine = levels[team.id].rating if team.id in levels else None
    scored = []
    for t in candidates:
        km = distances.get(t.neighborhood_key)
        band = distance_band(km) if km is not None else None
        theirs = levels[t.id].rating if t.id in levels else None
        points, reasons = suggestion_rules.score(suggestion_rules.Signals(
            distance_band=band, my_level=mine, their_level=theirs, my_days=days[team.id], their_days=days[t.id],
            played_recently=t.id in recent))
        if suggestion_rules.worth_suggesting(points, reasons):
            scored.append((points, t, band, theirs, reasons))
    scored.sort(key=lambda x: (-x[0], x[1].name_key, x[1].id))
    best = scored[:suggestion_rules.MAX_SUGGESTIONS]
    return [SuggestionView(team=summary(t), distance_band=band, level=round(level) if level is not None else None,
                           reasons=reasons) for _p, t, band, level, reasons in best]
