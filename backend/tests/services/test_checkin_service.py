from datetime import timedelta

import pytest

from app.domain.errors import ConflictError, DomainError, NotFoundError, PermissionDeniedError
from app.persistence.models_audit import AuditEvent
from app.persistence.models_matchday import MatchCheckIn
from app.services import booking_service, checkin_service, venue_queries, venue_service
from tests.services.test_team_service import new_user
from tests.services.venue_helpers import accepted_contract, signed_venue_match, slot_around, venue_with_court

LAT, LON = 10.9878, -74.7889  # cancha de prueba


@pytest.fixture
def s(ctx):
    scene = signed_venue_match(ctx)
    owner, venue, court = venue_with_court(ctx)
    booking = booking_service.request(ctx, scene["guest_owner"], scene["contract_id"],
                                      slot_around(ctx, owner, court, scene["kickoff"]).id)
    booking_service.decide(ctx, owner, booking.id, confirm=True)
    scene.update(owner=owner, venue=venue)
    return scene


def go_to(clock, moment):
    clock.advance(moment - clock.now())


def test_venue_owner_sets_location(ctx, s):
    with pytest.raises(PermissionDeniedError):
        venue_service.set_location(ctx, s["host_owner"], s["venue"].id, LAT, LON)
    with pytest.raises(DomainError):
        venue_service.set_location(ctx, s["owner"], s["venue"].id, 91, LON)
    assert not venue_queries.venue_detail(ctx, s["owner"], s["venue"].id).has_location
    venue_service.set_location(ctx, s["owner"], s["venue"].id, LAT, LON)
    assert venue_queries.venue_detail(ctx, s["owner"], s["venue"].id).has_location


def test_check_in_needs_venue_location_window_and_distance(ctx, s, clock):
    board = checkin_service.board(ctx, s["host_owner"], s["contract_id"])
    assert board.unavailable == "La cancha todavía no guardó su ubicación." and board.venue_name == "Canchas El Prado"
    venue_service.set_location(ctx, s["owner"], s["venue"].id, LAT, LON)
    with pytest.raises(ConflictError) as early:
        checkin_service.check_in(ctx, s["host_owner"], s["contract_id"], LAT, LON)
    assert early.value.code == "CHECKIN_NOT_OPEN"
    go_to(clock, s["kickoff"] - timedelta(minutes=30))
    with pytest.raises(DomainError) as far:  # unos 550 m al norte
        checkin_service.check_in(ctx, s["host_owner"], s["contract_id"], LAT + 0.005, LON)
    assert far.value.code == "NOT_AT_VENUE"
    first = checkin_service.check_in(ctx, s["host_owner"], s["contract_id"], LAT + 0.001, LON)  # unos 110 m
    clock.advance(timedelta(minutes=5))
    again = checkin_service.check_in(ctx, s["host_owner"], s["contract_id"], LAT, LON)
    assert again.checked_in_at == first.checked_in_at  # repetir no cambia la hora
    board = checkin_service.board(ctx, s["guest_owner"], s["contract_id"])
    assert ([i.display_name for i in board.items], board.window_open, board.me_checked_in) == (
        [s["host_owner"].display_name], True, False)
    go_to(clock, s["kickoff"] + timedelta(hours=3))
    with pytest.raises(ConflictError) as late:
        checkin_service.check_in(ctx, s["guest_owner"], s["contract_id"], LAT, LON)
    assert late.value.code == "CHECKIN_CLOSED"


def test_position_is_never_stored_or_audited(ctx, s, clock):
    venue_service.set_location(ctx, s["owner"], s["venue"].id, LAT, LON)
    go_to(clock, s["kickoff"] - timedelta(minutes=10))
    checkin_service.check_in(ctx, s["guest_owner"], s["contract_id"], LAT + 0.0004, LON - 0.0003)
    event = ctx.db.query(AuditEvent).filter(AuditEvent.action == "CHECKED_IN").one()
    assert "10.98" not in (event.after_json or "") and "latitude" not in (event.after_json or "")
    assert {c.name for c in MatchCheckIn.__table__.columns} == {"id", "contract_id", "user_id", "checked_in_at"}


def test_only_participants_and_only_with_confirmed_venue(ctx, s):
    with pytest.raises(NotFoundError):
        checkin_service.board(ctx, new_user(ctx, "curioso@r.test"), s["contract_id"])
    tres_owner, tres = s["city"]["tres"]
    lejos_owner, lejos = s["city"]["lejos"]
    informal = accepted_contract(ctx, (tres_owner, tres), (lejos_owner, lejos))  # sin cancha reservada
    assert checkin_service.board(ctx, tres_owner, informal).unavailable == (
        "Solo hay check-in en partidos con cancha reservada y confirmada.")
    with pytest.raises(ConflictError) as no_venue:
        checkin_service.check_in(ctx, tres_owner, informal, LAT, LON)
    assert no_venue.value.code == "NO_CONFIRMED_VENUE"
