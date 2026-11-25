"""Datos de la carta del jugador (Sprint 20): media, nivel, tripletes, últimos resultados e insignias."""

from sqlalchemy import select

from app.domain import card_rules
from app.domain.result_rules import ResultStatus
from app.persistence.models_contracts import MatchContract
from app.persistence.models_manager import MatchAppearance
from app.persistence.models_results import MatchResult
from app.services import achievement_queries
from app.services.context import ServiceContext
from app.services.manager_views import CardFaceView, PlayerStats

RECENT = 5


def face(ctx: ServiceContext, user_id: int, stats: PlayerStats, rating_average: float | None,
         votes: int) -> CardFaceView:
    rows = ctx.db.execute(select(MatchAppearance, MatchContract, MatchResult)
                          .join(MatchContract, MatchContract.id == MatchAppearance.contract_id)
                          .join(MatchResult, MatchResult.contract_id == MatchContract.id)
                          .where(MatchAppearance.user_id == user_id, MatchResult.status == ResultStatus.CONFIRMED)
                          .order_by(MatchResult.confirmed_at.desc(), MatchResult.id.desc())).all()
    recent = []
    for appearance, contract, result in rows[:RECENT]:
        mine, theirs = result.host_score or 0, result.guest_score or 0
        if appearance.team_id == contract.guest_team_id:
            mine, theirs = theirs, mine
        recent.append("W" if mine > theirs else "D" if mine == theirs else "L")
    level = card_rules.tier(stats.matches)
    earned = [b.name for b in achievement_queries.for_player(ctx, user_id) if b.earned_at is not None]
    return CardFaceView(
        media=card_rules.media(stats.matches, stats.wins, stats.goals, rating_average, votes),
        tier=level.name, next_tier=level.next_name, matches_to_next=level.matches_to_next,
        hat_tricks=sum(1 for a, _c, _r in rows if a.goals >= 3), recent=recent, badges=earned)
