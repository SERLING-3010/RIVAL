"""Pruebas de los hallazgos de la revisión independiente del Sprint 2."""

from datetime import timedelta

import pytest

from app.domain.errors import ConflictError, DomainError, NotFoundError
from app.domain.geo import SearchScope
from app.services import (
    free_agent_service,
    invitation_service,
    join_service,
    match_offer_service,
    match_request_service,
    team_service,
)
from app.services.inputs import JoinRequestInput
from tests.services.match_helpers import offer_input, request_input, setup_city
from tests.services.test_team_service import new_user, team_input


def test_offer_outside_publisher_scope_is_not_found(ctx):
    city = setup_city(ctx)
    owner, team = city["uno"]
    request = match_request_service.create_request(ctx, owner, team.id, request_input(ctx, radius=2))
    far_owner, far = city["lejos"]
    with pytest.raises(NotFoundError):
        match_offer_service.make_offer(ctx, far_owner, far.id, request.id, offer_input(ctx))
    other_city_owner = new_user(ctx, "otra@r.test")
    other = team_service.create_team(ctx, other_city_owner, team_input())
    with pytest.raises(NotFoundError):
        match_offer_service.make_offer(ctx, other_city_owner, other.id, request.id, offer_input(ctx))


def test_offer_in_the_past_rejected(ctx, clock):
    city = setup_city(ctx)
    owner, team = city["uno"]
    request = match_request_service.create_request(ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY))
    clock.advance(timedelta(days=2))
    with pytest.raises(DomainError) as error:
        match_offer_service.make_offer(ctx, city["dos"][0], city["dos"][1].id, request.id, offer_input(ctx, hours=-1))
    assert error.value.code == "OFFER_IN_PAST"


def test_version_keeps_growing_after_withdraw(ctx):
    city = setup_city(ctx)
    owner, team = city["uno"]
    request = match_request_service.create_request(ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY))
    rival_owner, rival = city["dos"]
    first = match_offer_service.make_offer(ctx, rival_owner, rival.id, request.id, offer_input(ctx))
    match_offer_service.withdraw(ctx, rival_owner, first.id)
    again = match_offer_service.make_offer(ctx, rival_owner, rival.id, request.id, offer_input(ctx))
    assert again.version == 2


def test_challenge_other_city_rejected(ctx):
    city = setup_city(ctx)
    owner, team = city["uno"]
    other = team_service.create_team(ctx, new_user(ctx, "otra@r.test"), team_input())
    with pytest.raises(DomainError) as error:
        match_request_service.create_request(
            ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY, target=other.id))
    assert error.value.code == "INVALID_CHALLENGE"


def test_admin_counter_ignores_invitations(ctx):
    captain, player = new_user(ctx, "cap@r.test"), new_user(ctx, "libre@r.test")
    team = team_service.create_team(ctx, captain, team_input())
    free_agent_service.set_free_agent(ctx, player, "FOOTBALL", active=True, position=None, note=None)
    invitation_service.invite(ctx, captain, team.id, player.id, None)
    assert team_service.my_teams(ctx, captain)[0].pending_requests == 0


def test_joining_by_request_removes_free_agent(ctx):
    captain, player = new_user(ctx, "cap@r.test"), new_user(ctx, "libre@r.test")
    team = team_service.create_team(ctx, captain, team_input())
    free_agent_service.set_free_agent(ctx, player, "FOOTBALL", active=True, position=None, note=None)
    request = join_service.request_join(ctx, player, team.id, JoinRequestInput())
    join_service.decide(ctx, captain, request.id, approve=True)
    assert free_agent_service.search(ctx, captain, sport_code="FOOTBALL", city="Barranquilla").total == 0


def test_reinvite_after_rejection_waits_a_week(ctx, clock):
    captain, player = new_user(ctx, "cap@r.test"), new_user(ctx, "libre@r.test")
    team = team_service.create_team(ctx, captain, team_input())
    free_agent_service.set_free_agent(ctx, player, "FOOTBALL", active=True, position=None, note=None)
    first = invitation_service.invite(ctx, captain, team.id, player.id, None)
    invitation_service.respond(ctx, player, first.id, accept=False)
    with pytest.raises(ConflictError) as error:
        invitation_service.invite(ctx, captain, team.id, player.id, None)
    assert error.value.code == "INVITATION_COOLDOWN"
    clock.advance(timedelta(days=8))
    invitation_service.invite(ctx, captain, team.id, player.id, None)

