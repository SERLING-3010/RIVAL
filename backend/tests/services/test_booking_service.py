from datetime import timedelta

import pytest

from app.domain.errors import ConflictError, DomainError, NotFoundError, PermissionDeniedError
from app.persistence.models_venues import Booking
from app.services import booking_service, contract_queries, contract_service, health_service, venue_queries
from tests.services.venue_helpers import (
    accepted_contract, sign_at_venue, signed_venue_match, slot_around, venue_owner, venue_with_court,
)


@pytest.fixture
def s(ctx):
    scene = signed_venue_match(ctx)
    owner, venue, court = venue_with_court(ctx)
    scene.update(owner=owner, venue=venue, court=court, slot=slot_around(ctx, owner, court, scene["kickoff"]))
    return scene


def contract(ctx, s):
    return contract_queries.get_contract(ctx, s["guest_owner"], s["contract_id"])


def test_request_then_confirm_makes_contract_ready(ctx, s):
    assert (contract(ctx, s).ready_to_play, contract(ctx, s).booking) == (False, None)
    booking = booking_service.request(ctx, s["guest_owner"], s["contract_id"], s["slot"].id)
    assert contract(ctx, s).booking.status == "PENDING"
    pending = venue_queries.venue_detail(ctx, s["owner"], s["venue"].id).pending_bookings
    assert [(b.id, b.host_name, b.guest_name) for b in pending] == [(booking.id, "Águilas", "Bravos")]
    with pytest.raises(PermissionDeniedError):
        booking_service.decide(ctx, s["guest_owner"], booking.id, confirm=True)
    booking_service.decide(ctx, s["owner"], booking.id, confirm=True)
    view = contract(ctx, s)
    assert (view.booking.status, view.booking.venue_name, view.ready_to_play) == ("CONFIRMED", "Canchas El Prado", True)
    assert venue_queries.venue_detail(ctx, s["guest_owner"], s["venue"].id).slots == []  # ya no está libre


def test_one_confirmation_per_slot(ctx, s):
    first = booking_service.request(ctx, s["guest_owner"], s["contract_id"], s["slot"].id)
    tres, lejos = s["city"]["tres"], s["city"]["lejos"]
    other_id = accepted_contract(ctx, tres, lejos)
    sign_at_venue(ctx, tres[0], lejos[0], other_id)
    second = booking_service.request(ctx, tres[0], other_id, s["slot"].id)
    booking_service.decide(ctx, s["owner"], first.id, confirm=True)
    ctx.db.refresh(second)
    assert second.status == "REJECTED"  # confirmar rechaza las demás pendientes de la franja
    with pytest.raises(ConflictError) as taken:
        booking_service.request(ctx, tres[0], other_id, s["slot"].id)
    assert taken.value.code == "SLOT_TAKEN"


def test_slot_must_cover_match_and_contract_must_be_signed(ctx, s):
    short = slot_around(ctx, s["owner"], s["court"], s["kickoff"] + timedelta(hours=3), before=0, after=45)
    with pytest.raises(DomainError) as cover:
        booking_service.request(ctx, s["guest_owner"], s["contract_id"], short.id)
    assert cover.value.code == "SLOT_DOES_NOT_COVER_MATCH"
    unsigned = accepted_contract(ctx, s["city"]["tres"], s["city"]["lejos"])
    with pytest.raises(ConflictError) as not_signed:
        booking_service.request(ctx, s["city"]["tres"][0], unsigned, s["slot"].id)
    assert not_signed.value.code == "CONTRACT_NOT_SIGNED"


def test_outsiders_and_duplicate_requests(ctx, s):
    with pytest.raises(NotFoundError):
        booking_service.request(ctx, venue_owner(ctx, "x@r.test"), s["contract_id"], s["slot"].id)
    booking_service.request(ctx, s["guest_owner"], s["contract_id"], s["slot"].id)
    with pytest.raises(ConflictError) as twice:
        booking_service.request(ctx, s["host_owner"], s["contract_id"], s["slot"].id)
    assert twice.value.code == "BOOKING_ALREADY_ACTIVE"


def test_cancelling_match_cancels_booking_and_requester_can_cancel(ctx, s):
    booking = booking_service.request(ctx, s["guest_owner"], s["contract_id"], s["slot"].id)
    booking_service.cancel(ctx, s["guest_owner"], booking.id)
    again = booking_service.request(ctx, s["host_owner"], s["contract_id"], s["slot"].id)
    booking_service.decide(ctx, s["owner"], again.id, confirm=True)
    contract_service.cancel(ctx, s["host_owner"], s["contract_id"], reason="Se lesionaron varios")
    ctx.db.refresh(again)
    assert again.status == "CANCELLED"


def test_health_detects_booking_that_no_longer_covers_match(ctx, s):
    booking = booking_service.request(ctx, s["guest_owner"], s["contract_id"], s["slot"].id)
    booking_service.decide(ctx, s["owner"], booking.id, confirm=True)
    assert health_service.run_checks(ctx) == []
    moved = slot_around(ctx, s["owner"], s["court"], s["kickoff"] + timedelta(days=1))
    ctx.db.execute(Booking.__table__.update().where(Booking.id == booking.id).values(slot_id=moved.id))
    assert [f.code for f in health_service.run_checks(ctx)] == ["BOOKING_OUT_OF_SYNC"]
