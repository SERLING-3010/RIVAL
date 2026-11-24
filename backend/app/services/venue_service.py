"""Registro de establecimientos, canchas y franjas (Sprint 6, RIV-012). Solo el dueño los gestiona."""

from datetime import datetime

from sqlalchemy import select

from app.domain.errors import DomainError, NotFoundError, PermissionDeniedError
from app.domain.geo import validate_coordinates
from app.domain.identity_rules import validate_place_name
from app.domain.roles import UserRole
from app.domain.text_keys import search_key
from app.domain.venue_rules import slots_overlap, validate_address, validate_reference_price, validate_slot
from app.persistence.models_identity import UserAccount
from app.persistence.models_venues import Court, Slot, Venue
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.venue_views import CourtInput, VenueInput


def create_venue(ctx: ServiceContext, actor: UserAccount, data: VenueInput) -> Venue:
    if not any(r.role == UserRole.VENUE_OWNER for r in actor.roles):
        raise PermissionDeniedError("VENUE_OWNER_ROLE_REQUIRED",
                                    "Agrega el rol de establecimiento para registrar tus canchas.")
    name = " ".join(data.name.split())
    if not 3 <= len(name) <= 60:
        raise DomainError("INVALID_VENUE_NAME", "El nombre del establecimiento debe tener entre 3 y 60 caracteres.")
    city = validate_place_name(data.city, "ciudad")
    venue = Venue(
        owner_id=actor.id, name=name, name_key=search_key(name), address=validate_address(data.address),
        city=city, city_key=search_key(city), neighborhood=validate_place_name(data.neighborhood, "barrio"),
        reference_price=validate_reference_price(data.reference_price), created_at=ctx.clock.now(),
    )
    ctx.db.add(venue)
    ctx.db.flush()
    record_event(ctx, action="VENUE_CREATED", entity="venue", entity_id=venue.id, initiated_by=actor.id,
                 after={"name": name, "city": city, "reference_price": venue.reference_price})
    return venue


def owned_venue(ctx: ServiceContext, actor: UserAccount, venue_id: int, lock: bool = False) -> Venue:
    venue = ctx.db.get(Venue, venue_id, with_for_update=lock)
    if venue is None or venue.status != "ACTIVE":
        raise NotFoundError("VENUE_NOT_FOUND", "El establecimiento no existe.")
    if venue.owner_id != actor.id:
        raise PermissionDeniedError("VENUE_OWNER_ONLY", "Solo el dueño del establecimiento puede hacer esto.")
    return venue


def add_court(ctx: ServiceContext, actor: UserAccount, venue_id: int, data: CourtInput) -> Court:
    venue = owned_venue(ctx, actor, venue_id)
    if not ctx.catalog.has_sport(data.sport_code):
        raise DomainError("UNKNOWN_SPORT", "Ese deporte no está en el catálogo.")
    name = " ".join(data.name.split())
    if not 1 <= len(name) <= 40:
        raise DomainError("INVALID_COURT_NAME", "El nombre de la cancha debe tener entre 1 y 40 caracteres.")
    court = Court(venue_id=venue.id, name=name, sport_code=data.sport_code,
                  surface=(data.surface or "").strip()[:40] or None)
    ctx.db.add(court)
    ctx.db.flush()
    record_event(ctx, action="COURT_ADDED", entity="venue", entity_id=venue.id, initiated_by=actor.id,
                 after={"court_id": court.id, "name": name, "sport": court.sport_code})
    return court


def add_slot(ctx: ServiceContext, actor: UserAccount, court_id: int, starts_at: datetime, ends_at: datetime) -> Slot:
    court = ctx.db.get(Court, court_id)
    if court is None:
        raise NotFoundError("COURT_NOT_FOUND", "La cancha no existe.")
    owned_venue(ctx, actor, court.venue_id, lock=True)  # en serie: dos franjas nuevas no se cruzan
    validate_slot(starts_at, ends_at, ctx.clock.now())
    for other in ctx.db.scalars(select(Slot).where(Slot.court_id == court.id, Slot.ends_at > starts_at,
                                                   Slot.starts_at < ends_at)):
        if slots_overlap((other.starts_at, other.ends_at), (starts_at, ends_at)):
            raise DomainError("SLOT_OVERLAP", "Ya hay una franja en esa cancha que se cruza con este horario.")
    slot = Slot(court_id=court.id, starts_at=starts_at, ends_at=ends_at, created_at=ctx.clock.now())
    ctx.db.add(slot)
    ctx.db.flush()
    record_event(ctx, action="SLOT_PUBLISHED", entity="venue", entity_id=court.venue_id, initiated_by=actor.id,
                 after={"slot_id": slot.id, "court_id": court.id, "starts_at": starts_at.isoformat(),
                        "ends_at": ends_at.isoformat()})
    return slot


def set_location(ctx: ServiceContext, actor: UserAccount, venue_id: int, latitude: float, longitude: float) -> Venue:
    """El dueño fija la ubicación de su establecimiento (un negocio, no una persona) para el check-in."""
    venue = owned_venue(ctx, actor, venue_id, lock=True)
    validate_coordinates(latitude, longitude)
    venue.latitude, venue.longitude = round(latitude, 6), round(longitude, 6)
    ctx.db.flush()
    record_event(ctx, action="VENUE_LOCATION_SET", entity="venue", entity_id=venue.id, initiated_by=actor.id,
                 after={"latitude": venue.latitude, "longitude": venue.longitude})
    return venue
