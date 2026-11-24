"""Esquemas de establecimientos, canchas, franjas y reservas (Sprint 6)."""

from decimal import Decimal

from pydantic import AwareDatetime, BaseModel, Field

from app.api.schemas_auth import StrictModel


class CreateVenueBody(StrictModel):
    name: str = Field(max_length=80)
    address: str = Field(max_length=150)
    city: str = Field(max_length=60)
    neighborhood: str = Field(max_length=60)
    reference_price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)


class CourtBody(StrictModel):
    name: str = Field(max_length=40)
    sport_code: str = Field(max_length=30)
    surface: str | None = Field(default=None, max_length=40)


class SlotBody(StrictModel):
    starts_at: AwareDatetime
    ends_at: AwareDatetime


class BookingBody(StrictModel):
    slot_id: int


class VenueSummaryOut(BaseModel):
    id: int
    name: str
    address: str
    city: str
    neighborhood: str
    reference_price: Decimal | None
    sports: list[str]


class CourtOut(BaseModel):
    id: int
    name: str
    sport_code: str
    surface: str | None


class SlotOut(BaseModel):
    id: int
    court_id: int
    court_name: str
    sport_code: str
    starts_at: AwareDatetime
    ends_at: AwareDatetime


class BookingOut(BaseModel):
    id: int
    status: str
    contract_id: int
    venue_id: int
    venue_name: str
    address: str
    slot: SlotOut
    host_name: str
    guest_name: str
    requested_at: AwareDatetime


class VenueDetailOut(BaseModel):
    venue: VenueSummaryOut
    is_owner: bool
    courts: list[CourtOut]
    slots: list[SlotOut]
    pending_bookings: list[BookingOut]
    confirmed_bookings: list[BookingOut]


class VenuePageOut(BaseModel):
    items: list[VenueSummaryOut]
    page: int
    page_size: int
    total: int
