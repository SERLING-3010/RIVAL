"""Rutas de establecimientos (canchas y franjas) y de reservas ligadas al contrato del partido."""

from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.dependencies import CtxDep, UserDep
from app.api.routes_contracts import contract_out
from app.api.schemas_contracts import ContractOut
from app.api.schemas_venues import (
    BookingBody, CourtBody, CreateVenueBody, SlotBody, VenueDetailOut, VenuePageOut, VenueSummaryOut,
)
from app.persistence.models_identity import UserAccount
from app.services import booking_service, venue_queries, venue_service
from app.services.context import ServiceContext
from app.services.venue_views import CourtInput, VenueInput, VenueSearchInput

router = APIRouter(prefix="/api/v1")


def _detail(ctx: ServiceContext, user: UserAccount, venue_id: int) -> VenueDetailOut:
    return VenueDetailOut.model_validate(asdict(venue_queries.venue_detail(ctx, user, venue_id)))


@router.post("/venues", status_code=201)
def create_venue(body: CreateVenueBody, ctx: CtxDep, user: UserDep) -> VenueDetailOut:
    venue = venue_service.create_venue(ctx, user, VenueInput(**body.model_dump()))
    return _detail(ctx, user, venue.id)


@router.get("/venues")
def search_venues(
    ctx: CtxDep,
    _user: UserDep,
    city: Annotated[str | None, Query(max_length=60)] = None,
    sport: Annotated[str | None, Query(max_length=30)] = None,
    q: Annotated[str | None, Query(max_length=60)] = None,
    page: Annotated[int, Query(ge=1, le=1000)] = 1,
) -> VenuePageOut:
    result = venue_queries.search_venues(ctx, VenueSearchInput(city=city, sport_code=sport, query=q, page=page))
    return VenuePageOut.model_validate(asdict(result))


@router.get("/me/venues")
def my_venues(ctx: CtxDep, user: UserDep) -> list[VenueSummaryOut]:
    return [VenueSummaryOut.model_validate(asdict(v)) for v in venue_queries.my_venues(ctx, user)]


@router.get("/venues/{venue_id}")
def venue_detail(venue_id: int, ctx: CtxDep, user: UserDep) -> VenueDetailOut:
    return _detail(ctx, user, venue_id)


@router.post("/venues/{venue_id}/courts", status_code=201)
def add_court(venue_id: int, body: CourtBody, ctx: CtxDep, user: UserDep) -> VenueDetailOut:
    venue_service.add_court(ctx, user, venue_id, CourtInput(**body.model_dump()))
    return _detail(ctx, user, venue_id)


@router.post("/courts/{court_id}/slots", status_code=201)
def add_slot(court_id: int, body: SlotBody, ctx: CtxDep, user: UserDep) -> VenueDetailOut:
    slot = venue_service.add_slot(ctx, user, court_id, body.starts_at, body.ends_at)
    return _detail(ctx, user, venue_queries.slot_venue_id(ctx, slot.id))


@router.post("/contracts/{contract_id}/bookings", status_code=201)
def request_booking(contract_id: int, body: BookingBody, ctx: CtxDep, user: UserDep) -> ContractOut:
    booking_service.request(ctx, user, contract_id, body.slot_id)
    return contract_out(ctx, user, contract_id)


@router.post("/bookings/{booking_id}/confirm")
def confirm_booking(booking_id: int, ctx: CtxDep, user: UserDep) -> VenueDetailOut:
    booking = booking_service.decide(ctx, user, booking_id, confirm=True)
    return _detail(ctx, user, venue_queries.slot_venue_id(ctx, booking.slot_id))


@router.post("/bookings/{booking_id}/reject")
def reject_booking(booking_id: int, ctx: CtxDep, user: UserDep) -> VenueDetailOut:
    booking = booking_service.decide(ctx, user, booking_id, confirm=False)
    return _detail(ctx, user, venue_queries.slot_venue_id(ctx, booking.slot_id))


@router.post("/bookings/{booking_id}/cancel")
def cancel_booking(booking_id: int, ctx: CtxDep, user: UserDep) -> ContractOut:
    booking = booking_service.cancel(ctx, user, booking_id)
    return contract_out(ctx, user, booking.contract_id)
