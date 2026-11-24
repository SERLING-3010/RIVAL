from datetime import timedelta

import pytest

from app.domain.errors import ConflictError, DomainError, NotFoundError, PermissionDeniedError
from app.persistence.models_contracts import MatchContract
from app.services import contract_queries, contract_service, fixture_service, referee_service, result_service
from tests.services.league_match_helpers import first_kickoff, league_with_teams
from tests.services.test_team_service import new_user


@pytest.fixture
def s(ctx):
    scene = league_with_teams(ctx)
    fixtures = fixture_service.generate(ctx, scene["organizer"], scene["league"].id, first_kickoff(ctx), 7)
    scene["contract"] = ctx.db.get(MatchContract, fixtures[0].contract_id)
    c = scene["contract"]
    owners = {t.id: o for o, t in scene["teams"].values()}
    scene["host_owner"], scene["guest_owner"] = owners[c.host_team_id], owners[c.guest_team_id]
    return scene


def sign_and_kickoff(ctx, clock, s):
    for owner in (s["host_owner"], s["guest_owner"]):
        contract_service.sign(ctx, owner, s["contract"].id, version=1)
    clock.advance(timedelta(days=3))


def test_assign_accept_and_referee_sees_match(ctx, s):
    with pytest.raises(PermissionDeniedError):
        referee_service.assign(ctx, s["host_owner"] if s["host_owner"] != s["organizer"] else s["guest_owner"],
                               s["contract"].id, s["referee"].id)
    assignment = referee_service.assign(ctx, s["organizer"], s["contract"].id, s["referee"].id)
    with pytest.raises(ConflictError):
        referee_service.assign(ctx, s["organizer"], s["contract"].id, s["referee"].id)
    with pytest.raises(PermissionDeniedError):
        referee_service.respond(ctx, s["organizer"], assignment.id, accept=True)
    referee_service.respond(ctx, s["referee"], assignment.id, accept=True)
    mine = referee_service.my_matches(ctx, s["referee"])
    assert [(m.contract_id, m.status, m.league_name) for m in mine] == [(s["contract"].id, "ACCEPTED", "Liga del Prado")]
    view = contract_queries.get_contract(ctx, s["host_owner"], s["contract"].id)
    assert (view.referee.display_name, view.referee.status) == ("José Peña", "ACCEPTED")


def test_only_approved_league_referees(ctx, s):
    outsider = new_user(ctx, "noarbitro@r.test")
    with pytest.raises(DomainError) as error:
        referee_service.assign(ctx, s["organizer"], s["contract"].id, outsider.id)
    assert error.value.code == "NOT_LEAGUE_REFEREE"


def test_referee_result_confirms_and_resolves_dispute(ctx, s, clock):
    assignment = referee_service.assign(ctx, s["organizer"], s["contract"].id, s["referee"].id)
    with pytest.raises(PermissionDeniedError):  # sin aceptar no puede reportar
        referee_service.report_result(ctx, s["referee"], s["contract"].id, 1, 0)
    referee_service.respond(ctx, s["referee"], assignment.id, accept=True)
    with pytest.raises(ConflictError):  # contrato sin firmar
        referee_service.report_result(ctx, s["referee"], s["contract"].id, 1, 0)
    sign_and_kickoff(ctx, clock, s)
    result_service.report(ctx, s["host_owner"], s["contract"].id, 3, 0)
    result_service.report(ctx, s["guest_owner"], s["contract"].id, 0, 3)
    assert contract_queries.get_contract(ctx, s["host_owner"], s["contract"].id).result.status == "DISPUTED"
    referee_service.report_result(ctx, s["referee"], s["contract"].id, 2, 2)
    result = contract_queries.get_contract(ctx, s["host_owner"], s["contract"].id).result
    assert (result.status, result.host_score, result.guest_score, result.by_referee) == ("CONFIRMED", 2, 2, True)
    with pytest.raises(ConflictError):
        referee_service.report_result(ctx, s["referee"], s["contract"].id, 3, 2)


def test_not_for_friendly_matches(ctx, s):
    friendly = matched_scene_outside(ctx)
    with pytest.raises(ConflictError) as error:
        referee_service.assign(ctx, s["organizer"], friendly, s["referee"].id)
    assert error.value.code == "NOT_A_LEAGUE_MATCH"
    with pytest.raises(NotFoundError):
        referee_service.respond(ctx, s["referee"], 999, accept=True)


def matched_scene_outside(ctx):
    """Un amistoso entre dos equipos nuevos, fuera de la liga."""
    from tests.services.test_rival_service import make_team
    from tests.services.venue_helpers import accepted_contract
    return accepted_contract(ctx, make_team(ctx, "x1@r.test", "Xenon", "Barrio Uno"),
                             make_team(ctx, "x2@r.test", "Yaguar", "Barrio Uno"))
