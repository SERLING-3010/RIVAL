"""Calendario de la liga (Sprint 8): todos contra todos; cada partido nace como contrato de la liga.

Lo genera una sola vez el organizador o un coorganizador. Los contratos nacen con árbitro y lugar
por acordar: los dos administradores los ajustan y firman como cualquier otro partido.
"""

from datetime import datetime

from sqlalchemy import select

from app.domain.contract_rules import default_terms
from app.domain.errors import ConflictError, PermissionDeniedError
from app.domain.fixture_rules import round_dates, round_robin
from app.domain.league_rules import EnrollmentStatus, StaffRole
from app.domain.match_rules import PlaceKind, RefereeMode
from app.persistence.models_contracts import MatchContract
from app.persistence.models_identity import UserAccount
from app.persistence.models_league_matches import LeagueFixture
from app.persistence.models_leagues import LeagueTeam
from app.services import contract_service
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.league_queries import get_league, staff_role


def generate(ctx: ServiceContext, actor: UserAccount, league_id: int, first_kickoff: datetime,
             days_between: int) -> list[LeagueFixture]:
    league = get_league(ctx, league_id, lock=True)
    if staff_role(ctx, league.id, actor.id) not in (StaffRole.ORGANIZER, StaffRole.CO_ORGANIZER):
        raise PermissionDeniedError("ORGANIZER_ONLY", "Solo el organizador o un coorganizador arma el calendario.")
    if ctx.db.scalar(select(LeagueFixture.id).where(LeagueFixture.league_id == league.id).limit(1)) is not None:
        raise ConflictError("FIXTURE_ALREADY_EXISTS", "Esta liga ya tiene calendario.")
    teams = list(ctx.db.scalars(select(LeagueTeam.team_id).where(
        LeagueTeam.league_id == league.id, LeagueTeam.status == EnrollmentStatus.APPROVED).order_by(LeagueTeam.id)))
    rounds = round_robin(teams)
    dates = round_dates(first_kickoff, days_between, len(rounds), ctx.clock.now())
    fixtures: list[LeagueFixture] = []
    for number, (pairs, kickoff) in enumerate(zip(rounds, dates, strict=True), start=1):
        for host_id, guest_id in pairs:
            contract = contract_service.create_contract(ctx, MatchContract(
                league_id=league.id, host_team_id=host_id, guest_team_id=guest_id, sport_code=league.sport_code,
                modality_code=league.modality_code), default_terms(kickoff, RefereeMode.WITH, PlaceKind.TO_AGREE, None),
                actor.id)
            fixture = LeagueFixture(league_id=league.id, round=number, contract_id=contract.id,
                                    host_team_id=host_id, guest_team_id=guest_id)
            ctx.db.add(fixture)
            fixtures.append(fixture)
    ctx.db.flush()
    record_event(ctx, action="LEAGUE_FIXTURE_GENERATED", entity="league", entity_id=league.id, initiated_by=actor.id,
                 after={"rounds": len(rounds), "matches": len(fixtures), "first": first_kickoff.isoformat(),
                        "days_between": days_between})
    return fixtures
