from datetime import timedelta

from app.services import (
    booking_service, callup_service, contract_service, join_service, lineup_service, pending_service, result_service,
    transfer_listing_service, transfer_service,
)
from app.services.inputs import JoinRequestInput
from tests.services.contract_helpers import matched_scene
from tests.services.manager_helpers import add_player, confirmed_match
from tests.services.test_team_service import new_user
from tests.services.venue_helpers import signed_venue_match, slot_around, venue_with_court


def kinds(ctx, user):
    return [i.kind for i in pending_service.pending(ctx, user)]


def test_signatures_then_results_are_pending_for_admins(ctx, clock):
    s = matched_scene(ctx)
    assert kinds(ctx, s["host_owner"]) == ["SIGN_CONTRACT"] == kinds(ctx, s["guest_owner"])
    item = pending_service.pending(ctx, s["host_owner"])[0]
    assert (item.target, item.target_id) == ("contract", s["contract_id"]) and "Bravos" in item.title
    contract_service.sign(ctx, s["host_owner"], s["contract_id"], version=1)
    assert kinds(ctx, s["host_owner"]) == [] and kinds(ctx, s["guest_owner"]) == ["SIGN_CONTRACT"]
    contract_service.sign(ctx, s["guest_owner"], s["contract_id"], version=1)
    clock.advance(timedelta(hours=31))
    assert kinds(ctx, s["host_owner"]) == ["REPORT_RESULT"]
    result_service.report(ctx, s["host_owner"], s["contract_id"], 1, 0)
    assert kinds(ctx, s["host_owner"]) == [] and kinds(ctx, s["guest_owner"]) == ["REPORT_RESULT"]
    result_service.report(ctx, s["guest_owner"], s["contract_id"], 0, 1)
    assert kinds(ctx, s["host_owner"]) == ["RESULT_DISPUTED"]
    assert kinds(ctx, s["city"]["tres"][0]) == []  # a un tercero no le toca nada


def test_callup_join_request_and_transfer(ctx):
    s = matched_scene(ctx)
    player = add_player(ctx, s["host"], "nueve@r.test")
    callup_service.call_up(ctx, s["host_owner"], s["contract_id"], [player.id])
    assert kinds(ctx, player) == ["CALLUP"]
    callup_service.respond(ctx, player, s["contract_id"], going=True)
    assert kinds(ctx, player) == []
    join_service.request_join(ctx, new_user(ctx, "quiere@r.test"), s["host"].id, JoinRequestInput())
    assert "JOIN_REQUESTS" in kinds(ctx, s["host_owner"])
    transfer_listing_service.set_listed(ctx, s["host_owner"], s["host"].id, player.id, listed=True)
    offer = transfer_service.make_offer(ctx, s["guest_owner"], s["guest"].id, player.id, 100)
    assert "TRANSFER_OWNER" in kinds(ctx, s["host_owner"])
    transfer_service.decide_owner(ctx, s["host_owner"], offer.id, accept=True)
    assert kinds(ctx, player) == ["TRANSFER_PLAYER"]


def test_venue_owner_sees_bookings_to_confirm(ctx):
    s = signed_venue_match(ctx)
    owner, _venue, court = venue_with_court(ctx)
    slot = slot_around(ctx, owner, court, s["kickoff"])
    booking_service.request(ctx, s["guest_owner"], s["contract_id"], slot.id)
    assert kinds(ctx, owner) == ["CONFIRM_BOOKING"]


def test_rate_teammates_after_confirmed_match(ctx, clock):
    s = confirmed_match(ctx, clock, 1, 0)
    striker = add_player(ctx, s["host"], "nueve@r.test")
    lineup_service.record(ctx, s["host_owner"], s["contract_id"], [(striker.id, 1), (s["host_owner"].id, 0)])
    assert kinds(ctx, striker) == ["RATE_TEAMMATES"]
    clock.advance(timedelta(days=8))
    assert kinds(ctx, striker) == []  # pasó la ventana de 7 días


def test_rivals_ordered_by_similar_level(ctx, clock):
    from app.domain.geo import SearchScope
    from app.persistence.models_matchday import TeamRating
    from app.services import rival_service

    s = confirmed_match(ctx, clock, 4, 0)  # Águilas sube, Bravos baja
    uno = s["host"]
    ctx.db.add(TeamRating(team_id=s["city"]["tres"][1].id, rating=1700.0, rd=200.0, volatility=0.06, matches=3,
                          updated_at=ctx.clock.now()))
    ctx.db.flush()
    page = rival_service.search_rivals(ctx, s["host_owner"], uno.id, SearchScope.CITY, by_level=True)
    names = [r.team.name for r in page.items]
    assert names[0] == "Cóndores" and names[-1] == "Lejanos"  # el más parecido primero; sin nivel al final
    assert page.items[0].level == 1700 and page.items[-1].level is None
