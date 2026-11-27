import pytest

from app.domain.errors import ConflictError, NotFoundError, PermissionDeniedError
from app.domain.geo import SearchScope
from app.services import block_service, match_feed_service, match_offer_service, match_request_service, rival_service
from tests.services.match_helpers import offer_input, request_input, setup_city


@pytest.fixture
def s(ctx):
    return setup_city(ctx)


def names(page):
    return [r.team.name for r in page.items]


def test_block_hides_both_ways_and_stops_challenges_and_offers(ctx, s):
    (uno_owner, uno), (dos_owner, dos) = s["uno"], s["dos"]
    request = match_request_service.create_request(ctx, uno_owner, uno.id, request_input(ctx, scope=SearchScope.CITY))
    block_service.block(ctx, uno_owner, uno.id, dos.id)
    assert "Bravos" not in names(rival_service.search_rivals(ctx, uno_owner, uno.id, SearchScope.CITY))
    assert "Águilas" not in names(rival_service.search_rivals(ctx, dos_owner, dos.id, SearchScope.CITY))
    assert match_feed_service.open_requests_for(ctx, dos_owner, dos.id, SearchScope.CITY, 5) == []
    with pytest.raises(NotFoundError):
        match_offer_service.make_offer(ctx, dos_owner, dos.id, request.id, offer_input(ctx))
    with pytest.raises(NotFoundError):
        match_request_service.create_request(ctx, dos_owner, dos.id,
                                             request_input(ctx, scope=SearchScope.CITY, target=uno.id))
    block_service.unblock(ctx, uno_owner, uno.id, dos.id)
    assert "Bravos" in names(rival_service.search_rivals(ctx, uno_owner, uno.id, SearchScope.CITY))


def test_only_admin_blocks_and_not_self_or_twice(ctx, s):
    (uno_owner, uno), (dos_owner, dos) = s["uno"], s["dos"]
    with pytest.raises(PermissionDeniedError):
        block_service.block(ctx, dos_owner, uno.id, dos.id)
    with pytest.raises(ConflictError):
        block_service.block(ctx, uno_owner, uno.id, uno.id)
    block_service.block(ctx, uno_owner, uno.id, dos.id)
    with pytest.raises(ConflictError):
        block_service.block(ctx, uno_owner, uno.id, dos.id)
    assert [b.team.name for b in block_service.blocked_by(ctx, uno_owner, uno.id)] == ["Bravos"]
