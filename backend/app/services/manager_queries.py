"""Lectura del modo manager: ficha del jugador, mercado, ofertas del jugador y vista del equipo."""

from collections.abc import Iterable

from sqlalchemy import select

from app.domain.errors import NotFoundError
from app.domain.manager_rules import ACTIVE_TRANSFERS, TransferStatus
from app.domain.result_rules import ResultStatus
from app.domain.team_rules import resolve_admin
from app.domain.text_keys import search_key
from app.persistence.models_contracts import MatchContract
from app.persistence.models_identity import UserAccount
from app.persistence.models_manager import MatchAppearance, TransferListing, TransferOffer
from app.persistence.models_results import MatchResult
from app.persistence.models_teams import Team
from app.services import coin_service
from app.services.context import ServiceContext
from app.services.manager_views import (
    CoinEntryView, MarketItemView, PlayerCardView, PlayerStats, SquadMemberView, TeamManagerView, TransferOfferView,
)
from app.services.rival_service import require_member
from app.services.team_service import get_active_team, member_views, summary


def stats_for(ctx: ServiceContext, user_ids: Iterable[int]) -> dict[int, PlayerStats]:
    """Estadísticas reales: solo partidos con resultado confirmado y con el jugador en la planilla."""
    totals: dict[int, list[int]] = {u: [0, 0, 0, 0, 0] for u in user_ids}
    rows = ctx.db.execute(select(MatchAppearance, MatchContract, MatchResult)
                          .join(MatchContract, MatchContract.id == MatchAppearance.contract_id)
                          .join(MatchResult, MatchResult.contract_id == MatchContract.id)
                          .where(MatchAppearance.user_id.in_(list(totals)),
                                 MatchResult.status == ResultStatus.CONFIRMED))
    for appearance, contract, result in rows:
        mine, theirs = result.host_score or 0, result.guest_score or 0
        if appearance.team_id == contract.guest_team_id:
            mine, theirs = theirs, mine
        t = totals[appearance.user_id]
        t[0], t[1] = t[0] + 1, t[1] + appearance.goals
        t[2 if mine > theirs else 3 if mine == theirs else 4] += 1
    return {u: PlayerStats(*t) for u, t in totals.items()}


def player_card(ctx: ServiceContext, _actor: UserAccount, user_id: int) -> PlayerCardView:
    user = ctx.db.get(UserAccount, user_id)
    if user is None:
        raise NotFoundError("PLAYER_NOT_FOUND", "Ese jugador no existe.")
    teams = ctx.db.scalars(select(Team).where(Team.status == "ACTIVE", Team.memberships.any(user_id=user_id)))
    s = stats_for(ctx, [user_id])[user_id]
    return PlayerCardView(user_id=user.id, display_name=user.display_name, position=user.position,
                          sports=sorted(x.sport_code for x in user.sports), teams=[summary(t) for t in teams],
                          matches=s.matches, goals=s.goals, wins=s.wins, draws=s.draws, losses=s.losses)


def market(ctx: ServiceContext, _actor: UserAccount, sport: str, city: str | None) -> list[MarketItemView]:
    stmt = (select(TransferListing, Team, UserAccount).join(Team, Team.id == TransferListing.team_id)
            .join(UserAccount, UserAccount.id == TransferListing.user_id)
            .where(Team.status == "ACTIVE", Team.sport_code == sport))
    if city:
        stmt = stmt.where(Team.city_key == search_key(city))
    rows = ctx.db.execute(stmt.order_by(TransferListing.listed_at.desc()).limit(100)).all()
    stats = stats_for(ctx, [u.id for _, _, u in rows])
    return [MarketItemView(player_id=u.id, display_name=u.display_name, position=u.position, team=summary(t),
                           matches=stats[u.id].matches, goals=stats[u.id].goals) for _, t, u in rows]


def _offer_views(ctx: ServiceContext, offers: Iterable[TransferOffer]) -> list[TransferOfferView]:
    result = []
    for o in offers:
        player, src, dst = ctx.db.get(UserAccount, o.player_id), ctx.db.get(Team, o.from_team_id), ctx.db.get(Team, o.to_team_id)
        assert player and src and dst
        result.append(TransferOfferView(id=o.id, player_id=player.id, player_name=player.display_name,
                                        from_team=summary(src), to_team=summary(dst), amount=o.amount,
                                        status=o.status, created_at=o.created_at))
    return result


def offer_view(ctx: ServiceContext, offer_id: int) -> TransferOfferView:
    offer = ctx.db.get(TransferOffer, offer_id)
    if offer is None:
        raise NotFoundError("TRANSFER_OFFER_NOT_FOUND", "La oferta de traspaso no existe.")
    return _offer_views(ctx, [offer])[0]


def my_offers(ctx: ServiceContext, actor: UserAccount) -> list[TransferOfferView]:
    """Ofertas que esperan la decisión del propio jugador."""
    return _offer_views(ctx, ctx.db.scalars(select(TransferOffer).where(
        TransferOffer.player_id == actor.id, TransferOffer.status == TransferStatus.PENDING_PLAYER)))


def team_manager(ctx: ServiceContext, actor: UserAccount, team_id: int) -> TeamManagerView:
    team = get_active_team(ctx, team_id)
    require_member(team, actor)
    is_admin = resolve_admin(member_views(team)) == actor.id
    ids = [m.user_id for m in team.memberships]
    users = {u.id: u for u in ctx.db.scalars(select(UserAccount).where(UserAccount.id.in_(ids)))}
    listed = set(ctx.db.scalars(select(TransferListing.user_id).where(TransferListing.team_id == team.id)))
    stats = stats_for(ctx, ids)
    squad = [SquadMemberView(user_id=m.user_id, display_name=users[m.user_id].display_name, role=m.role,
                             position=users[m.user_id].position, listed=m.user_id in listed,
                             matches=stats[m.user_id].matches, goals=stats[m.user_id].goals)
             for m in sorted(team.memberships, key=lambda m: (m.joined_at, m.id))]

    def offers(column: object) -> list[TransferOfferView]:
        if not is_admin:
            return []
        return _offer_views(ctx, ctx.db.scalars(select(TransferOffer).where(
            column == team.id, TransferOffer.status.in_(ACTIVE_TRANSFERS)).order_by(TransferOffer.id.desc())))
    history = [CoinEntryView(amount=e.amount, reason=e.reason, reference=e.reference, created_at=e.created_at)
               for e in coin_service.history(ctx, team.id)]
    return TeamManagerView(team=summary(team), is_admin=is_admin, balance=coin_service.balance(ctx, team.id),
                           history=history, squad=squad, offers_received=offers(TransferOffer.from_team_id),
                           offers_sent=offers(TransferOffer.to_team_id))

