from datetime import timedelta

import pytest

from app.domain.errors import ConflictError, DomainError, PermissionDeniedError
from app.domain.geo import SearchScope
from app.domain.match_rules import RefereeMode
from app.services import match_offer_service, match_request_service
from tests.services.match_helpers import offer_input, request_input, setup_city


@pytest.fixture
def scene(ctx):
    city = setup_city(ctx)
    owner, team = city["uno"]
    request = match_request_service.create_request(ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY))
    return city, request


def test_counter_offer_creates_new_version(ctx, scene):
    city, request = scene
    rival_owner, rival = city["dos"]
    first = match_offer_service.make_offer(ctx, rival_owner, rival.id, request.id, offer_input(ctx, hours=30))
    second = match_offer_service.make_offer(ctx, rival_owner, rival.id, request.id, offer_input(ctx, hours=40))
    assert (first.status, second.version) == ("SUPERSEDED", 2)


def test_offer_outside_window_or_wrong_referee_rejected(ctx, scene):
    city, request = scene
    rival_owner, rival = city["dos"]
    with pytest.raises(DomainError) as outside:
        match_offer_service.make_offer(ctx, rival_owner, rival.id, request.id, offer_input(ctx, hours=200))
    assert outside.value.code == "OFFER_OUTSIDE_WINDOW"
    with pytest.raises(DomainError) as referee:
        match_offer_service.make_offer(ctx, rival_owner, rival.id, request.id, offer_input(ctx, referee=RefereeMode.EITHER))
    assert referee.value.code == "REFEREE_MODE_REQUIRED"


def test_cannot_offer_to_own_request(ctx, scene):
    city, request = scene
    owner, team = city["uno"]
    with pytest.raises(ConflictError):
        match_offer_service.make_offer(ctx, owner, team.id, request.id, offer_input(ctx))


def test_accept_closes_request_and_supersedes_others(ctx, scene):
    city, request = scene
    owner, _ = city["uno"]
    winner = match_offer_service.make_offer(ctx, city["dos"][0], city["dos"][1].id, request.id, offer_input(ctx))
    loser = match_offer_service.make_offer(ctx, city["tres"][0], city["tres"][1].id, request.id, offer_input(ctx))
    with pytest.raises(PermissionDeniedError):
        match_offer_service.decide(ctx, city["dos"][0], winner.id, accept=True)
    match_offer_service.decide(ctx, owner, winner.id, accept=True)
    assert (request.status, request.accepted_offer_id, loser.status) == ("MATCHED", winner.id, "SUPERSEDED")
    with pytest.raises(ConflictError):
        match_offer_service.make_offer(ctx, city["lejos"][0], city["lejos"][1].id, request.id, offer_input(ctx))


def test_withdraw_and_cancel(ctx, scene):
    city, request = scene
    owner, _ = city["uno"]
    offer = match_offer_service.make_offer(ctx, city["dos"][0], city["dos"][1].id, request.id, offer_input(ctx))
    other = match_offer_service.make_offer(ctx, city["tres"][0], city["tres"][1].id, request.id, offer_input(ctx))
    match_offer_service.withdraw(ctx, city["dos"][0], offer.id)
    match_request_service.cancel_request(ctx, owner, request.id)
    assert (offer.status, other.status, request.status) == ("WITHDRAWN", "CANCELLED", "CANCELLED")


def test_offers_visibility(ctx, scene):
    city, request = scene
    owner, _ = city["uno"]
    match_offer_service.make_offer(ctx, city["dos"][0], city["dos"][1].id, request.id, offer_input(ctx))
    match_offer_service.make_offer(ctx, city["tres"][0], city["tres"][1].id, request.id, offer_input(ctx))
    assert len(match_offer_service.list_offers(ctx, owner, request.id)) == 2
    assert [o.team.name for o in match_offer_service.list_offers(ctx, city["dos"][0], request.id)] == ["Bravos"]
    assert match_offer_service.list_offers(ctx, city["lejos"][0], request.id) == []


def test_cannot_accept_after_expiry(ctx, scene, clock):
    city, request = scene
    owner, _ = city["uno"]
    offer = match_offer_service.make_offer(ctx, city["dos"][0], city["dos"][1].id, request.id, offer_input(ctx))
    clock.advance(timedelta(days=5))
    with pytest.raises(ConflictError) as error:
        match_offer_service.decide(ctx, owner, offer.id, accept=True)
    assert error.value.code == "MATCH_REQUEST_CLOSED"
