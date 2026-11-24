from datetime import timedelta

import pytest

from app.domain.errors import ConflictError, DomainError, PermissionDeniedError
from app.domain.geo import SearchScope
from app.services import match_feed_service, match_request_service
from tests.services.match_helpers import request_input, setup_city
from tests.services.test_team_service import new_user


def test_nearby_request_visible_only_within_radius(ctx):
    city = setup_city(ctx)
    owner, team = city["uno"]
    match_request_service.create_request(ctx, owner, team.id, request_input(ctx, radius=2))
    for key, expected in (("dos", 1), ("tres", 0), ("lejos", 0)):
        viewer, viewer_team = city[key]
        feed = match_feed_service.open_requests_for(ctx, viewer, viewer_team.id, SearchScope.CITY)
        assert len(feed) == expected, key
    viewer, viewer_team = city["dos"]
    item = match_feed_service.open_requests_for(ctx, viewer, viewer_team.id, SearchScope.CITY)[0]
    assert item.distance_band == "UNDER_2_KM"
    assert item.team.neighborhood == "Barrio Uno"


def test_city_request_visible_to_whole_city(ctx):
    city = setup_city(ctx)
    owner, team = city["uno"]
    match_request_service.create_request(ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY))
    viewer, viewer_team = city["lejos"]
    assert len(match_feed_service.open_requests_for(ctx, viewer, viewer_team.id, SearchScope.CITY)) == 1


def test_direct_challenge_only_seen_by_target(ctx):
    city = setup_city(ctx)
    owner, team = city["uno"]
    target_owner, target = city["lejos"]
    match_request_service.create_request(
        ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY, target=target.id))
    assert len(match_feed_service.open_requests_for(ctx, target_owner, target.id, SearchScope.NEIGHBORHOOD)) == 1
    other_owner, other = city["dos"]
    assert match_feed_service.open_requests_for(ctx, other_owner, other.id, SearchScope.CITY) == []


def test_only_admin_creates_requests(ctx):
    city = setup_city(ctx)
    _, team = city["uno"]
    outsider = new_user(ctx, "x@r.test")
    with pytest.raises(PermissionDeniedError):
        match_request_service.create_request(ctx, outsider, team.id, request_input(ctx))


def test_invalid_window_rejected(ctx):
    city = setup_city(ctx)
    owner, team = city["uno"]
    data = request_input(ctx)
    data.window_end = data.window_start - timedelta(hours=1)
    with pytest.raises(DomainError) as error:
        match_request_service.create_request(ctx, owner, team.id, data)
    assert error.value.code == "WINDOW_INVERTED"


def test_max_three_open_requests(ctx):
    city = setup_city(ctx)
    owner, team = city["uno"]
    for _ in range(3):
        match_request_service.create_request(ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY))
    with pytest.raises(ConflictError) as error:
        match_request_service.create_request(ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY))
    assert error.value.code == "TOO_MANY_OPEN_REQUESTS"


def test_expired_request_leaves_feed(ctx, clock):
    city = setup_city(ctx)
    owner, team = city["uno"]
    match_request_service.create_request(ctx, owner, team.id, request_input(ctx, scope=SearchScope.CITY))
    clock.advance(timedelta(days=4))
    viewer, viewer_team = city["dos"]
    assert match_feed_service.open_requests_for(ctx, viewer, viewer_team.id, SearchScope.CITY) == []
    assert match_request_service.team_requests(ctx, owner, team.id)[0].status == "EXPIRED"
