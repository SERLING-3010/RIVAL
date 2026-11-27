"""Carta del equipo (Sprint 23): básica por la media de los titulares y especiales por hazañas del equipo.

Las especiales se otorgan la primera vez que se ve la plantilla cumpliendo los requisitos [SUPUESTO]
y quedan para siempre, aunque la media baje. Solo cuentan partidos con resultado confirmado.
"""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError

from app.domain import card_rules, special_cards, team_look_rules, team_special_cards
from app.domain.result_rules import ResultStatus
from app.persistence.models_cards import TeamSpecialCard
from app.persistence.models_contracts import MatchContract
from app.persistence.models_cup import LeagueCup
from app.persistence.models_leagues import League
from app.persistence.models_results import MatchResult
from app.persistence.models_teams import Team
from app.services import settlement_service
from app.services.context import ServiceContext
from app.services.manager_views import FeatGoalView, SpecialCardView


@dataclass(frozen=True)
class TeamCardView:
    tier: str  # básica por la media de los titulares
    next_tier: str | None
    media_to_next: int
    display_tier: str  # la elegida por el equipo, o su mejor especial, o la básica
    chosen: str | None  # elección guardada: un código, "BASIC" o None (automático)
    available: list[str]  # lo que puede elegir: "BASIC" y sus especiales ganadas
    goals: int
    clean_sheets: int
    cups: int
    leagues: int
    specials: list[SpecialCardView]  # las quince, ganadas o no


def _scores(ctx: ServiceContext, team_id: int) -> list[tuple[int, int]]:
    rows = ctx.db.execute(select(MatchContract, MatchResult).join(MatchResult, MatchResult.contract_id ==
                                                                   MatchContract.id)
                          .where(MatchResult.status == ResultStatus.CONFIRMED,
                                 or_(MatchContract.host_team_id == team_id, MatchContract.guest_team_id == team_id))
                          .order_by(MatchResult.confirmed_at, MatchResult.id))
    return [((r.host_score or 0, r.guest_score or 0) if c.host_team_id == team_id
             else (r.guest_score or 0, r.host_score or 0)) for c, r in rows]


def _city_rank(ctx: ServiceContext, team: Team) -> int | None:
    """Puesto por nivel (rating) entre los equipos activos de su ciudad; None si aún no tiene nivel."""
    ids = list(ctx.db.scalars(select(Team.id).where(Team.city_key == team.city_key, Team.status == "ACTIVE")))
    ratings = settlement_service.ratings_for(ctx, ids)
    mine = ratings.get(team.id)
    return None if mine is None else 1 + sum(1 for r in ratings.values() if r.rating > mine.rating)


def _award(ctx: ServiceContext, team_id: int, reached: list[str]) -> dict[str, datetime]:
    have = {c.code: c.earned_at for c in ctx.db.scalars(select(TeamSpecialCard)
                                                         .where(TeamSpecialCard.team_id == team_id))}
    now = ctx.clock.now()
    for code in reached:
        if code in have:
            continue
        try:
            with ctx.db.begin_nested():  # otra lectura simultánea pudo otorgarla primero
                ctx.db.add(TeamSpecialCard(team_id=team_id, code=code, earned_at=now))
        except IntegrityError:
            pass
        have[code] = now
    return have


def card(ctx: ServiceContext, team: Team, team_media: int) -> TeamCardView:
    champions = list(ctx.db.scalars(select(League.id).where(League.champion_team_id == team.id)))
    cup_leagues = set(ctx.db.scalars(select(LeagueCup.league_id).where(LeagueCup.champion_team_id == team.id)))
    city = _city_rank(ctx, team) if team_special_cards.needs_city_rank(team_media) else None
    feats = team_special_cards.feats_from_scores(_scores(ctx, team.id), cups=len(cup_leagues),
                                                 leagues=len(champions),
                                                 doubles=sum(1 for lid in champions if lid in cup_leagues),
                                                 city_rank=city)
    progress = team_special_cards.progress(feats)
    have = _award(ctx, team.id, [p.code for p in progress if p.reached(team_media)])
    level = card_rules.tier(team_media)
    owned = [code for code in special_cards.CODES if code in have]
    return TeamCardView(
        tier=level.name, next_tier=level.next_name, media_to_next=level.media_to_next,
        display_tier=team_look_rules.shown_design(team.card_choice, owned, level.name, special_cards.best(set(have))),
        chosen=team.card_choice, available=team_look_rules.available_designs(owned), goals=feats.goals,
        clean_sheets=feats.clean_sheets, cups=feats.cups, leagues=feats.leagues,
        specials=[SpecialCardView(p.code, p.min_media, have.get(p.code),
                                  [FeatGoalView(g.label, g.current, g.target) for g in p.goals]) for p in progress])
