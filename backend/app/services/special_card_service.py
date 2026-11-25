"""Cartas especiales del jugador (Sprint 23): hazañas, puesto en su ciudad y cartas ganadas.

Una carta especial se otorga la primera vez que se ve la carta del jugador cumpliendo sus requisitos
[SUPUESTO: no hace falta un proceso aparte]. Desde ahí es suya aunque la media baje.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.domain import card_rules, special_cards
from app.domain.special_cards import Feats
from app.persistence.models_cards import SpecialCard
from app.persistence.models_identity import UserAccount
from app.services import goal_claim_service, player_rating_service
from app.services.context import ServiceContext


def city_rank(ctx: ServiceContext, user_id: int, card_media: int) -> int:
    """1 + cuántos jugadores de su ciudad, con al menos un partido, tienen una media mayor."""
    from app.services.manager_queries import stats_for  # manager_queries usa este módulo

    user = ctx.db.get(UserAccount, user_id)
    assert user is not None
    others = list(ctx.db.scalars(select(UserAccount.id).where(UserAccount.city_key == user.city_key,
                                                              UserAccount.id != user_id)))
    better = 0
    for other, s in stats_for(ctx, others).items():
        if s.matches:
            average, votes = player_rating_service.summary(ctx, other)
            better += card_rules.media(s.matches, s.wins, s.goals, average, votes) > card_media
    return better + 1


def feats(ctx: ServiceContext, user_id: int, goals: int, per_match: list[int], cup_champion: bool,
          card_media: int) -> Feats:
    """per_match: goles del jugador en cada partido confirmado."""
    return Feats(goals=goals, hat_tricks=sum(g >= 3 for g in per_match), pokers=sum(g >= 4 for g in per_match),
                 manitas=sum(g >= 5 for g in per_match), kinds=goal_claim_service.confirmed_kinds(ctx, user_id),
                 cup_champion=cup_champion,
                 city_rank=city_rank(ctx, user_id, card_media) if special_cards.needs_city_rank(card_media) else None)


def owned(ctx: ServiceContext, user_ids: list[int]) -> dict[int, dict[str, datetime]]:
    result: dict[int, dict[str, datetime]] = {u: {} for u in user_ids}
    for card in ctx.db.scalars(select(SpecialCard).where(SpecialCard.user_id.in_(user_ids))):
        result[card.user_id][card.code] = card.earned_at
    return result


def award(ctx: ServiceContext, user_id: int, reached: list[str]) -> dict[str, datetime]:
    """Guarda las especiales recién alcanzadas y devuelve todas las que tiene, con su fecha."""
    have = owned(ctx, [user_id])[user_id]
    now = ctx.clock.now()
    for code in reached:
        if code in have:
            continue
        try:
            with ctx.db.begin_nested():  # otra lectura simultánea pudo otorgarla primero
                ctx.db.add(SpecialCard(user_id=user_id, code=code, earned_at=now))
        except IntegrityError:
            pass
        have[code] = now
    return have
