"""Lectura de establecimientos: directorio, detalle con franjas libres y reservas para el dueño."""

from sqlalchemy import func, select

from app.domain.errors import NotFoundError
from app.domain.text_keys import search_key
from app.domain.venue_rules import BookingStatus
from app.persistence.models_contracts import MatchContract
from app.persistence.models_identity import UserAccount
from app.persistence.models_teams import Team
from app.persistence.models_venues import Booking, Court, Slot, Venue
from app.services.context import ServiceContext
from app.services.venue_views import (
    BookingView, CourtView, SlotView, VenueDetailView, VenuePage, VenueSearchInput, VenueSummaryView,
)

MAX_PAGE_SIZE = 50
_CONFIRMED = BookingStatus.CONFIRMED.value


def get_venue(ctx: ServiceContext, venue_id: int) -> Venue:
    venue = ctx.db.get(Venue, venue_id)
    if venue is None or venue.status != "ACTIVE":
        raise NotFoundError("VENUE_NOT_FOUND", "El establecimiento no existe.")
    return venue


def venue_summary(ctx: ServiceContext, venue: Venue) -> VenueSummaryView:
    sports = sorted(set(ctx.db.scalars(select(Court.sport_code).where(Court.venue_id == venue.id))))
    return VenueSummaryView(id=venue.id, name=venue.name, address=venue.address, city=venue.city,
                            neighborhood=venue.neighborhood, reference_price=venue.reference_price, sports=sports)


def slot_view(slot: Slot, court: Court) -> SlotView:
    return SlotView(id=slot.id, court_id=court.id, court_name=court.name, sport_code=court.sport_code,
                    starts_at=slot.starts_at, ends_at=slot.ends_at)


def booking_view(ctx: ServiceContext, booking: Booking) -> BookingView:
    slot = ctx.db.get(Slot, booking.slot_id)
    court = ctx.db.get(Court, slot.court_id) if slot else None
    venue = ctx.db.get(Venue, court.venue_id) if court else None
    contract = ctx.db.get(MatchContract, booking.contract_id)
    assert slot and court and venue and contract
    host, guest = ctx.db.get(Team, contract.host_team_id), ctx.db.get(Team, contract.guest_team_id)
    return BookingView(id=booking.id, status=booking.status, contract_id=contract.id, venue_id=venue.id,
                       venue_name=venue.name, address=venue.address, slot=slot_view(slot, court),
                       host_name=host.name if host else "", guest_name=guest.name if guest else "",
                       requested_at=booking.requested_at)


def search_venues(ctx: ServiceContext, query: VenueSearchInput) -> VenuePage:
    page_size, page = max(1, min(query.page_size, MAX_PAGE_SIZE)), max(1, query.page)
    stmt = select(Venue).where(Venue.status == "ACTIVE")
    if query.city:
        stmt = stmt.where(Venue.city_key == search_key(query.city))
    if query.sport_code:
        stmt = stmt.where(select(Court.id).where(Court.venue_id == Venue.id,
                                                 Court.sport_code == query.sport_code).exists())
    if query.query:
        stmt = stmt.where(Venue.name_key.contains(search_key(query.query), autoescape=True))
    total = ctx.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = ctx.db.scalars(stmt.order_by(Venue.name_key, Venue.id).offset((page - 1) * page_size).limit(page_size))
    return VenuePage(items=[venue_summary(ctx, v) for v in rows], page=page, page_size=page_size, total=total)


def _bookings(ctx: ServiceContext, venue_id: int, status: str) -> list[BookingView]:
    rows = ctx.db.scalars(select(Booking).join(Slot, Slot.id == Booking.slot_id).join(Court, Court.id == Slot.court_id)
                          .where(Court.venue_id == venue_id, Booking.status == status,
                                 Slot.ends_at > ctx.clock.now())
                          .order_by(Slot.starts_at))
    return [booking_view(ctx, b) for b in rows]


def venue_detail(ctx: ServiceContext, actor: UserAccount, venue_id: int) -> VenueDetailView:
    venue = get_venue(ctx, venue_id)
    courts = list(ctx.db.scalars(select(Court).where(Court.venue_id == venue.id).order_by(Court.id)))
    by_id = {c.id: c for c in courts}
    taken = select(Booking.id).where(Booking.slot_id == Slot.id, Booking.status == _CONFIRMED).exists()
    slots = ctx.db.scalars(select(Slot).where(Slot.court_id.in_(by_id), Slot.starts_at > ctx.clock.now(), ~taken)
                           .order_by(Slot.starts_at, Slot.id).limit(100))
    is_owner = venue.owner_id == actor.id
    return VenueDetailView(
        venue=venue_summary(ctx, venue), is_owner=is_owner, has_location=venue.latitude is not None,
        courts=[CourtView(id=c.id, name=c.name, sport_code=c.sport_code, surface=c.surface) for c in courts],
        slots=[slot_view(s, by_id[s.court_id]) for s in slots],
        pending_bookings=_bookings(ctx, venue.id, BookingStatus.PENDING.value) if is_owner else [],
        confirmed_bookings=_bookings(ctx, venue.id, _CONFIRMED) if is_owner else [],
    )


def slot_venue_id(ctx: ServiceContext, slot_id: int) -> int:
    venue_id = ctx.db.scalar(select(Court.venue_id).join(Slot, Slot.court_id == Court.id).where(Slot.id == slot_id))
    assert venue_id is not None
    return venue_id


def my_venues(ctx: ServiceContext, actor: UserAccount) -> list[VenueSummaryView]:
    rows = ctx.db.scalars(select(Venue).where(Venue.owner_id == actor.id, Venue.status == "ACTIVE")
                          .order_by(Venue.name_key))
    return [venue_summary(ctx, v) for v in rows]
