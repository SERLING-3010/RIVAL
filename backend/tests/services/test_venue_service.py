from datetime import timedelta
from decimal import Decimal

import pytest

from app.domain.errors import DomainError, NotFoundError, PermissionDeniedError
from app.services import venue_queries, venue_service
from app.services.venue_views import CourtInput, VenueSearchInput
from tests.services.test_team_service import new_user
from tests.services.venue_helpers import venue_input, venue_owner, venue_with_court


def test_only_venue_owners_register_and_manage(ctx):
    with pytest.raises(PermissionDeniedError) as error:
        venue_service.create_venue(ctx, new_user(ctx, "jugador2@r.test"), venue_input())
    assert error.value.code == "VENUE_OWNER_ROLE_REQUIRED"
    owner, venue, court = venue_with_court(ctx)
    other = venue_owner(ctx, "otro@r.test")
    with pytest.raises(PermissionDeniedError):
        venue_service.add_court(ctx, other, venue.id, CourtInput(name="Cancha 2", sport_code="FOOTBALL"))
    with pytest.raises(DomainError) as sport:
        venue_service.add_court(ctx, owner, venue.id, CourtInput(name="Cancha 2", sport_code="CURLING"))
    assert sport.value.code == "UNKNOWN_SPORT"
    assert venue.reference_price == Decimal("80000.00")


def test_slots_cannot_overlap_on_same_court(ctx):
    owner, _venue, court = venue_with_court(ctx)
    start = ctx.clock.now() + timedelta(days=1)
    venue_service.add_slot(ctx, owner, court.id, start, start + timedelta(hours=1))
    venue_service.add_slot(ctx, owner, court.id, start + timedelta(hours=1), start + timedelta(hours=2))
    with pytest.raises(DomainError) as overlap:
        venue_service.add_slot(ctx, owner, court.id, start + timedelta(minutes=30), start + timedelta(minutes=90))
    assert overlap.value.code == "SLOT_OVERLAP"


def test_search_and_detail_show_open_future_slots(ctx, clock):
    owner, venue, court = venue_with_court(ctx)
    start = ctx.clock.now() + timedelta(hours=2)
    venue_service.add_slot(ctx, owner, court.id, start, start + timedelta(hours=1))
    page = venue_queries.search_venues(ctx, VenueSearchInput(city="ciudad prueba", sport_code="FOOTBALL"))
    assert [(v.name, v.sports) for v in page.items] == [("Canchas El Prado", ["FOOTBALL"])]
    visitor = new_user(ctx, "visita@r.test")
    detail = venue_queries.venue_detail(ctx, visitor, venue.id)
    assert ([s.court_name for s in detail.slots], detail.is_owner, detail.pending_bookings) == (["Cancha 1"], False, [])
    clock.advance(timedelta(hours=3))
    assert venue_queries.venue_detail(ctx, visitor, venue.id).slots == []
    assert [v.name for v in venue_queries.my_venues(ctx, owner)] == ["Canchas El Prado"]
    with pytest.raises(NotFoundError):
        venue_queries.venue_detail(ctx, visitor, 999)
