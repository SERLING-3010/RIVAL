"""Calendario y tabla de posiciones de la liga (Sprint 8). Visibles para cualquier usuario."""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select

from app.domain.result_rules import ResultStatus
from app.domain.standings_rules import MatchScore, StandingRow, standings
from app.persistence.models_contracts import MatchContract
from app.persistence.models_league_matches import LeagueFixture
from app.persistence.models_leagues import LeagueTeam
from app.persistence.models_results import MatchResult
from app.persistence.models_teams import Team
from app.services.context import ServiceContext
from app.services.contract_queries import get_version, terms_of
from app.services.league_queries import get_league
from app.services.team_service import summary
from app.services.team_views import TeamSummaryView


@dataclass(frozen=True)
class FixtureView:
    round: int
    contract_id: int
    host: TeamSummaryView
    guest: TeamSummaryView
    kickoff_at: datetime
    status: str  # estado del contrato: NEGOTIATING, SIGNED, CANCELLED
    result: str | None  # "2 – 1" solo si está confirmado


def calendar(ctx: ServiceContext, league_id: int) -> list[FixtureView]:
    league = get_league(ctx, league_id)
    rows = ctx.db.execute(select(LeagueFixture, MatchContract).join(MatchContract, MatchContract.id ==
                                                                     LeagueFixture.contract_id)
                          .where(LeagueFixture.league_id == league.id)
                          .order_by(LeagueFixture.round, LeagueFixture.id)).all()
    views = []
    for fixture, contract in rows:
        host, guest = ctx.db.get(Team, fixture.host_team_id), ctx.db.get(Team, fixture.guest_team_id)
        assert host and guest
        version = get_version(ctx, contract.signed_version_id or contract.current_version_id)
        result = ctx.db.scalar(select(MatchResult).where(MatchResult.contract_id == contract.id,
                                                         MatchResult.status == ResultStatus.CONFIRMED))
        views.append(FixtureView(round=fixture.round, contract_id=contract.id, host=summary(host),
                                 guest=summary(guest), kickoff_at=terms_of(version).kickoff_at, status=contract.status,
                                 result=f"{result.host_score} – {result.guest_score}" if result else None))
    return views


def table(ctx: ServiceContext, league_id: int) -> list[StandingRow]:
    league = get_league(ctx, league_id)
    team_ids = list(ctx.db.scalars(select(LeagueTeam.team_id).where(
        LeagueTeam.league_id == league.id, LeagueTeam.status == "APPROVED")))
    names = {t.id: t.name for t in ctx.db.scalars(select(Team).where(Team.id.in_(team_ids)))}
    rows = ctx.db.execute(select(MatchContract, MatchResult)  # solo el calendario cuenta; la copa no suma a la tabla
                          .join(MatchResult, MatchResult.contract_id == MatchContract.id)
                          .join(LeagueFixture, LeagueFixture.contract_id == MatchContract.id)
                          .where(LeagueFixture.league_id == league.id, MatchResult.status == ResultStatus.CONFIRMED))
    scores = [MatchScore(c.host_team_id, c.guest_team_id, r.host_score or 0, r.guest_score or 0) for c, r in rows]
    return standings(names, scores)
