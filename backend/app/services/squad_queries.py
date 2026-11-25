"""Plantilla del equipo en modo juego (Sprint 22): cartas de todos, titulares y encabezado del equipo.

Solo para miembros: incluye la alineación táctica, que el rival no debe ver. Los titulares salen de
la alineación guardada del próximo partido; si no hay, se sugiere una por media (marcada como tal).
"""

from dataclasses import dataclass

from sqlalchemy import func, select

from app.domain import card_rules, special_cards, tactics_rules
from app.domain.result_rules import ResultStatus
from app.persistence.models_contracts import MatchContract
from app.persistence.models_identity import UserAccount
from app.persistence.models_manager import MatchAppearance
from app.persistence.models_results import MatchResult
from app.persistence.models_tactics import MatchTactic, MatchTacticSlot
from app.services import achievement_queries, player_rating_service, settlement_service, special_card_service
from app.services import team_card_service
from app.services.team_card_service import TeamCardView
from app.services.context import ServiceContext
from app.services.manager_queries import stats_for
from app.services.contract_queries import is_admin_of
from app.services.rival_service import require_member
from app.services.team_service import get_active_team, summary
from app.services.team_views import TeamSummaryView


@dataclass(frozen=True)
class SquadCardView:
    user_id: int
    display_name: str
    position: str | None
    role: str  # COACH, CAPTAIN, PLAYER
    media: int
    tier: str
    matches: int
    goals: int
    wins: int
    rating_average: float | None  # las seis estadísticas de la carta grande (Sprint 22)
    hat_tricks: int
    badges: int


@dataclass(frozen=True)
class StarterView:
    user_id: int
    position: str | None


@dataclass(frozen=True)
class SquadView:
    team: TeamSummaryView
    media: int | None  # promedio de los titulares mostrados
    wins: int
    draws: int
    losses: int
    level: int | None
    badges: list[str]
    players_per_side: int
    formation: str | None
    suggested: bool  # True si los titulares son una sugerencia por media, no una alineación guardada
    starters: list[StarterView]
    subs: list[int]
    members: list[SquadCardView]
    card: TeamCardView | None  # Sprint 23: el diseño del cuadro de la media; None sin titulares
    crest: str | None  # escudo armado (team_look_rules); None = el predeterminado
    can_edit: bool  # el actor puede cambiar escudo y diseño (administrador del equipo)


def _saved_tactic(ctx: ServiceContext, team_id: int) -> MatchTactic | None:
    """La alineación más reciente de un partido no cancelado y aún sin resultado confirmado."""
    confirmed = select(MatchResult.contract_id).where(MatchResult.status == ResultStatus.CONFIRMED)
    return ctx.db.scalar(select(MatchTactic).join(MatchContract, MatchContract.id == MatchTactic.contract_id)
                         .where(MatchTactic.team_id == team_id, MatchContract.status != "CANCELLED",
                                MatchContract.id.not_in(confirmed))
                         .order_by(MatchTactic.updated_at.desc(), MatchTactic.id.desc()).limit(1))


def _record(ctx: ServiceContext, team_id: int) -> tuple[int, int, int]:
    rows = ctx.db.execute(select(MatchContract, MatchResult)
                          .join(MatchResult, MatchResult.contract_id == MatchContract.id)
                          .where((MatchContract.host_team_id == team_id) | (MatchContract.guest_team_id == team_id),
                                 MatchResult.status == ResultStatus.CONFIRMED)).all()
    w = d = loss = 0
    for c, r in rows:
        mine, theirs = (r.host_score or 0, r.guest_score or 0)
        if c.guest_team_id == team_id:
            mine, theirs = theirs, mine
        w, d, loss = w + (mine > theirs), d + (mine == theirs), loss + (mine < theirs)
    return w, d, loss


def _hat_tricks(ctx: ServiceContext, ids: list[int]) -> dict[int, int]:
    """Partidos con resultado confirmado en que cada jugador marcó 3 goles o más."""
    rows = ctx.db.execute(select(MatchAppearance.user_id, func.count())
                          .join(MatchResult, MatchResult.contract_id == MatchAppearance.contract_id)
                          .where(MatchAppearance.user_id.in_(ids), MatchAppearance.goals >= 3,
                                 MatchResult.status == ResultStatus.CONFIRMED)
                          .group_by(MatchAppearance.user_id)).all()
    return {user_id: int(count) for user_id, count in rows}


def squad(ctx: ServiceContext, actor: UserAccount, team_id: int) -> SquadView:
    team = get_active_team(ctx, team_id)
    require_member(team, actor)
    ids = [m.user_id for m in team.memberships]
    users = {u.id: u for u in ctx.db.scalars(select(UserAccount).where(UserAccount.id.in_(ids)))}
    stats, tricks = stats_for(ctx, ids), _hat_tricks(ctx, ids)
    owned = special_card_service.owned(ctx, ids)  # la carta se dibuja con su mejor especial (Sprint 23)
    members = []
    for m in team.memberships:
        s, (avg, votes) = stats[m.user_id], player_rating_service.summary(ctx, m.user_id)
        card_media = card_rules.media(s.matches, s.wins, s.goals, avg, votes)
        shown = special_cards.best(set(owned[m.user_id])) or card_rules.tier(card_media).name
        members.append(SquadCardView(m.user_id, users[m.user_id].display_name, users[m.user_id].position, m.role,
                                     card_media, shown, s.matches, s.goals, s.wins, avg,
                                     tricks.get(m.user_id, 0),
                                     sum(1 for b in achievement_queries.for_player(ctx, m.user_id) if b.earned_at)))
    members.sort(key=lambda c: (-c.media, c.display_name))
    per_side = ctx.catalog.players_per_side(team.sport_code, team.modality_code) or len(members)
    tactic = _saved_tactic(ctx, team.id)
    if tactic is not None:
        slots = list(ctx.db.scalars(select(MatchTacticSlot).where(MatchTacticSlot.tactic_id == tactic.id)
                                    .order_by(MatchTacticSlot.sort_order)))
        starters = [StarterView(s.user_id, s.position) for s in slots if s.starter and s.user_id in users]
        subs, formation = [s.user_id for s in slots if not s.starter and s.user_id in users], tactic.formation
    else:
        players = [c for c in members if c.role != "COACH"][:per_side]
        starters, subs = [StarterView(c.user_id, None) for c in players], []
        formation = next(iter(tactics_rules.suggested_formations(team.modality_code)), None)
    by_id = {c.user_id: c for c in members}
    shown = [by_id[s.user_id].media for s in starters]
    w, d, loss = _record(ctx, team.id)
    rating = settlement_service.ratings_for(ctx, [team.id]).get(team.id)
    media = round(sum(shown) / len(shown)) if shown else None
    return SquadView(team=summary(team), media=media, wins=w, draws=d,
                     losses=loss, level=round(rating.rating) if rating else None,
                     badges=[b.name for b in achievement_queries.for_team(ctx, team.id) if b.earned_at],
                     players_per_side=per_side, formation=formation, suggested=tactic is None,
                     starters=starters, subs=subs, members=members,
                     card=team_card_service.card(ctx, team, media) if media is not None else None,
                     crest=team.crest, can_edit=is_admin_of(team, actor))
