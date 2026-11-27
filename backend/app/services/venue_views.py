"""Entradas y vistas de establecimientos, canchas, franjas y reservas (Sprint 6)."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass
class VenueInput:
    name: str
    address: str
    city: str
    neighborhood: str
    reference_price: Decimal | None = None


@dataclass
class CourtInput:
    name: str
    sport_code: str
    surface: str | None = None


@dataclass
class VenueSearchInput:
    city: str | None = None
    sport_code: str | None = None
    query: str | None = None
    page: int = 1
    page_size: int = field(default=20)


@dataclass(frozen=True)
class VenueSummaryView:
    id: int
    name: str
    address: str
    city: str
    neighborhood: str
    reference_price: Decimal | None  # solo de referencia, por hora; el pago es fuera de la app
    sports: list[str]


@dataclass(frozen=True)
class CourtView:
    id: int
    name: str
    sport_code: str
    surface: str | None


@dataclass(frozen=True)
class SlotView:
    id: int
    court_id: int
    court_name: str
    sport_code: str
    starts_at: datetime
    ends_at: datetime


@dataclass(frozen=True)
class BookingView:
    id: int
    status: str
    contract_id: int
    venue_id: int
    venue_name: str
    address: str
    slot: SlotView
    host_name: str
    guest_name: str
    requested_at: datetime


@dataclass(frozen=True)
class VenueDetailView:
    venue: VenueSummaryView
    is_owner: bool
    has_location: bool  # para el check-in (Sprint 15)
    courts: list[CourtView]
    slots: list[SlotView]  # franjas futuras sin reserva confirmada
    pending_bookings: list[BookingView]  # solo para el dueño
    confirmed_bookings: list[BookingView]  # solo para el dueño


@dataclass(frozen=True)
class VenuePage:
    items: list[VenueSummaryView]
    page: int
    page_size: int
    total: int
