"""Cuadro de la copa (Sprint 16): lo ve cualquiera, como la liga; el organizador ve qué falta definir."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select

from app.domain import cup_rules
from app.domain.errors import NotFoundError
from app.domain.league_rules import StaffRole
from app.domain.result_rules import ResultStatus
from app.persistence.models_cup import CupMatch, LeagueCup
from app.persistence.models_identity import UserAccount
from app.persistence.models_results import MatchResult
from app.persistence.models_teams import Team
from app.services.context import ServiceContext
from app.services.league_queries import get_league, staff_role


@dataclass(frozen=True)
class CupMatchView:
    id: int
    position: int
    host_team_id: int | None
    guest_team_id: int | None
    host_name: str | None  # None: aún no se sabe (o pase directo en la primera ronda)
    guest_name: str | None
    contract_id: int | None
    host_score: int | None
    guest_score: int | None
    winner_name: str | None
    needs_tiebreak: bool


@dataclass(frozen=True)
class CupRoundView:
    number: int
    name: str
    planned_at: datetime
    matches: list[CupMatchView]


@dataclass(frozen=True)
class CupView:
    league_id: int
    champion_name: str | None
    can_manage: bool
    rounds: list[CupRoundView]


def bracket(ctx: ServiceContext, actor: UserAccount, league_id: int) -> CupView:
    league = get_league(ctx, league_id)
    cup = ctx.db.scalar(select(LeagueCup).where(LeagueCup.league_id == league.id))
    if cup is None:
        raise NotFoundError("CUP_NOT_FOUND", "Esta liga todavía no tiene copa.")
    matches = list(ctx.db.scalars(select(CupMatch).where(CupMatch.cup_id == cup.id)
                                  .order_by(CupMatch.round, CupMatch.position)))
    team_ids = {t for m in matches for t in (m.host_team_id, m.guest_team_id) if t is not None}
    names = {t.id: t.name for t in ctx.db.scalars(select(Team).where(Team.id.in_(team_ids)))}
    contracts = [m.contract_id for m in matches if m.contract_id is not None]
    results = {r.contract_id: r for r in ctx.db.scalars(select(MatchResult).where(
        MatchResult.contract_id.in_(contracts), MatchResult.status == ResultStatus.CONFIRMED))}

    def view(m: CupMatch) -> CupMatchView:
        r = results.get(m.contract_id or 0)
        return CupMatchView(
            id=m.id, position=m.position, host_team_id=m.host_team_id, guest_team_id=m.guest_team_id,
            host_name=names.get(m.host_team_id or 0),
            guest_name=names.get(m.guest_team_id or 0), contract_id=m.contract_id,
            host_score=r.host_score if r else None, guest_score=r.guest_score if r else None,
            winner_name=names.get(m.winner_team_id or 0),
            needs_tiebreak=bool(r and r.host_score == r.guest_score and m.winner_team_id is None))

    rounds = [CupRoundView(number=n, name=cup_rules.round_name(n, cup.rounds),
                           planned_at=cup.first_kickoff + timedelta(days=cup.days_between * (n - 1)),
                           matches=[view(m) for m in matches if m.round == n]) for n in range(1, cup.rounds + 1)]
    role = staff_role(ctx, league.id, actor.id)
    return CupView(league_id=league.id, champion_name=names.get(cup.champion_team_id or 0),
                   can_manage=role in (StaffRole.ORGANIZER, StaffRole.CO_ORGANIZER), rounds=rounds)
