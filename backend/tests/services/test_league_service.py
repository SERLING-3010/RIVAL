import pytest

from app.domain.errors import ConflictError, DomainError, NotFoundError, PermissionDeniedError
from app.domain.league_rules import StaffRole
from app.domain.roles import UserRole
from app.persistence.models_audit import AuditEvent
from app.services import auth_service, league_enrollment_service as enroll, league_queries, league_service
from app.services.league_views import LeagueInput, LeagueSearchInput
from tests.conftest import register_input
from tests.services.test_rival_service import make_team
from tests.services.test_team_service import new_user


def league_input(**changes):
    data = {"name": "Liga del Prado", "sport_code": "FOOTBALL", "modality_code": "F7",
            "city": "Ciudad Prueba", "season": "2026-2", "description": "Sábados en la tarde"}
    return LeagueInput(**{**data, **changes})


def referee(ctx, email="arbitro@r.test"):
    return auth_service.register_user(ctx, register_input(email=email, role=UserRole.REFEREE))


@pytest.fixture
def s(ctx):
    organizer, own_team = make_team(ctx, "org@r.test", "Águilas", "Barrio Uno")
    league = league_service.create_league(ctx, organizer, league_input())
    rival_owner, rival = make_team(ctx, "riv@r.test", "Bravos", "Barrio Dos")
    return {"organizer": organizer, "own": own_team, "league": league, "rival_owner": rival_owner, "rival": rival}


def detail(ctx, s, actor=None):
    return league_queries.league_detail(ctx, actor or s["organizer"], s["league"].id)


def test_creator_becomes_organizer_and_needs_team_or_referee_role(ctx, s):
    assert [(m.display_name, m.role) for m in detail(ctx, s).staff] == [("José Peña", "ORGANIZER")]
    with pytest.raises(PermissionDeniedError):
        league_service.create_league(ctx, new_user(ctx, "solo@r.test"), league_input())
    league_service.create_league(ctx, referee(ctx), league_input(name="Liga Arbitral"))
    with pytest.raises(DomainError) as unknown:
        league_service.create_league(ctx, s["organizer"], league_input(modality_code="B5X5"))
    assert unknown.value.code == "UNKNOWN_MODALITY"


def test_team_enrollment_approved_by_organizer(ctx, s):
    entry = enroll.request_team(ctx, s["rival_owner"], s["league"].id, s["rival"].id)
    with pytest.raises(ConflictError):
        enroll.request_team(ctx, s["rival_owner"], s["league"].id, s["rival"].id)
    assert detail(ctx, s, s["rival_owner"]).pending_teams == []  # solo el personal ve pendientes
    assert [e.team.name for e in detail(ctx, s).pending_teams] == ["Bravos"]
    with pytest.raises(PermissionDeniedError):
        enroll.decide(ctx, s["rival_owner"], "team", entry.id, approve=True)
    enroll.decide(ctx, s["organizer"], "team", entry.id, approve=True)
    assert [e.team.name for e in detail(ctx, s, s["rival_owner"]).teams] == ["Bravos"]


def test_team_must_match_league_and_be_requested_by_admin(ctx, s):
    _, basket = make_team(ctx, "bk@r.test", "Delfines", "Barrio Uno", modality="B5X5", sport="BASKETBALL")
    owner = ctx.db.get(type(s["organizer"]), basket.created_by)
    with pytest.raises(DomainError) as mismatch:
        enroll.request_team(ctx, owner, s["league"].id, basket.id)
    assert mismatch.value.code == "TEAM_NOT_ELIGIBLE"
    with pytest.raises(PermissionDeniedError):
        enroll.request_team(ctx, s["organizer"], s["league"].id, s["rival"].id)


def test_referee_joins_and_coordinator_can_approve(ctx, s):
    ref, coordinator = referee(ctx), new_user(ctx, "coord@r.test")
    with pytest.raises(PermissionDeniedError) as not_referee:
        enroll.request_referee(ctx, s["rival_owner"], s["league"].id)
    assert not_referee.value.code == "REFEREE_ROLE_REQUIRED"
    entry = enroll.request_referee(ctx, ref, s["league"].id)
    with pytest.raises(PermissionDeniedError):
        enroll.decide(ctx, coordinator, "referee", entry.id, approve=True)
    league_service.add_staff(ctx, s["organizer"], s["league"].id, coordinator.id, StaffRole.REFEREE_COORDINATOR)
    with pytest.raises(PermissionDeniedError):  # el coordinador no decide inscripciones de equipos
        enroll.decide(ctx, coordinator, "team", enroll.request_team(
            ctx, s["rival_owner"], s["league"].id, s["rival"].id).id, approve=True)
    enroll.decide(ctx, coordinator, "referee", entry.id, approve=True)
    assert [r.display_name for r in detail(ctx, s).referees] == ["José Peña"]


def test_withdraw_and_leave_then_request_again(ctx, s):
    entry = enroll.request_team(ctx, s["rival_owner"], s["league"].id, s["rival"].id)
    enroll.withdraw(ctx, s["rival_owner"], "team", entry.id)
    again = enroll.request_team(ctx, s["rival_owner"], s["league"].id, s["rival"].id)
    enroll.decide(ctx, s["organizer"], "team", again.id, approve=True)
    enroll.withdraw(ctx, s["rival_owner"], "team", again.id)  # un aprobado puede salir
    assert detail(ctx, s).teams == []
    with pytest.raises(ConflictError):
        enroll.withdraw(ctx, s["rival_owner"], "team", again.id)


def test_only_organizer_adds_staff_and_once(ctx, s):
    helper = new_user(ctx, "co@r.test")
    with pytest.raises(PermissionDeniedError):
        league_service.add_staff(ctx, s["rival_owner"], s["league"].id, helper.id, StaffRole.CO_ORGANIZER)
    league_service.add_staff(ctx, s["organizer"], s["league"].id, helper.id, StaffRole.CO_ORGANIZER)
    with pytest.raises(ConflictError):
        league_service.add_staff(ctx, s["organizer"], s["league"].id, helper.id, StaffRole.REFEREE_COORDINATOR)
    with pytest.raises(NotFoundError):
        league_service.add_staff(ctx, s["organizer"], s["league"].id, 9999, StaffRole.CO_ORGANIZER)


def test_search_my_leagues_and_audit(ctx, s):
    page = league_queries.search_leagues(ctx, LeagueSearchInput(sport_code="FOOTBALL", city="ciudad prueba", query="prado"))
    assert [l.name for l in page.items] == ["Liga del Prado"]
    entry = enroll.request_team(ctx, s["rival_owner"], s["league"].id, s["rival"].id)
    enroll.decide(ctx, s["organizer"], "team", entry.id, approve=False)
    assert [(m.league.name, m.relation) for m in league_queries.my_leagues(ctx, s["organizer"])] == [
        ("Liga del Prado", "ORGANIZER")]
    actions = [e.action for e in ctx.db.query(AuditEvent).filter(AuditEvent.entity.like("league%"))]
    assert actions == ["LEAGUE_CREATED", "LEAGUE_TEAM_REQUESTED", "LEAGUE_TEAM_REJECTED"]
