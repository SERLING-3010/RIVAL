"""Ayudas de pruebas de liga con calendario [SIMULACIÓN]: tres equipos aprobados y un árbitro aprobado."""

from datetime import timedelta

from app.domain.roles import UserRole
from app.services import auth_service, contract_service, league_enrollment_service as enroll, league_service
from app.services import result_service
from app.services.league_views import LeagueInput
from tests.conftest import register_input
from tests.services.test_rival_service import make_team


def league_with_teams(ctx):
    teams = {k: make_team(ctx, f"{k}@r.test", name, "Barrio Uno")
             for k, name in (("a", "Águilas"), ("b", "Bravos"), ("c", "Cóndores"))}
    organizer = teams["a"][0]
    league = league_service.create_league(ctx, organizer, LeagueInput(
        name="Liga del Prado", sport_code="FOOTBALL", modality_code="F7", city="Ciudad Prueba", season="2026-2"))
    for owner, team in teams.values():
        entry = enroll.request_team(ctx, owner, league.id, team.id)
        enroll.decide(ctx, organizer, "team", entry.id, approve=True)
    referee = auth_service.register_user(ctx, register_input(email="arbitro@r.test", role=UserRole.REFEREE))
    entry = enroll.request_referee(ctx, referee, league.id)
    enroll.decide(ctx, organizer, "referee", entry.id, approve=True)
    return {"league": league, "teams": teams, "organizer": organizer, "referee": referee}


def first_kickoff(ctx):
    return ctx.clock.now() + timedelta(days=2)


def play(ctx, clock, contract, owners, host_goals, guest_goals):
    """Ambos firman, pasa la hora y los dos reportan el mismo marcador."""
    for owner in owners:
        contract_service.sign(ctx, owner, contract.id, version=1)
    clock.advance(timedelta(days=3))
    for owner in owners:
        result_service.report(ctx, owner, contract.id, host_goals, guest_goals)
