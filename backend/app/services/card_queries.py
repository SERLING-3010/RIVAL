"""Datos de la carta del jugador (Sprints 20 y 23): media, carta básica, especiales, valor e insignias."""

from sqlalchemy import func, select

from app.domain import card_rules, special_cards
from app.domain.result_rules import ResultStatus
from app.persistence.models_contracts import MatchContract
from app.persistence.models_manager import MatchAppearance
from app.persistence.models_matchday import MatchCheckIn
from app.persistence.models_results import MatchResult
from app.services import achievement_queries, special_card_service
from app.services.context import ServiceContext
from app.services.manager_views import CardFaceView, FeatGoalView, PlayerStats, SpecialCardView

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
    card_media = card_rules.media(stats.matches, stats.wins, stats.goals, rating_average, votes)
    level = card_rules.tier(card_media)
    badges = [b for b in achievement_queries.for_player(ctx, user_id) if b.earned_at is not None]
    feats = special_card_service.feats(ctx, user_id, stats.goals, [a.goals for a, _c, _r in rows],
                                       any(b.code == "CUP_CHAMPION" for b in badges), card_media)
    progress = special_cards.progress(feats)
    have = special_card_service.award(ctx, user_id, [p.code for p in progress if p.reached(card_media)])
    specials = [SpecialCardView(p.code, p.min_media, have.get(p.code),
                                [FeatGoalView(g.label, g.current, g.target) for g in p.goals]) for p in progress]
    return CardFaceView(
        media=card_media, tier=level.name, next_tier=level.next_name, media_to_next=level.media_to_next,
        display_tier=special_cards.best(set(have)) or level.name,
        market_value=card_rules.market_value(card_media, level.rank, len(have), recent), specials=specials,
        hat_tricks=sum(1 for a, _c, _r in rows if a.goals >= 3), recent=recent, badges=[b.name for b in badges],
        check_ins=ctx.db.scalar(select(func.count()).select_from(MatchCheckIn)
                                .where(MatchCheckIn.user_id == user_id)) or 0)
