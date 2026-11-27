"""Reserva de una franja para el partido: la pide un equipo, la confirma el establecimiento.

Pedir, confirmar y cancelar bloquean la fila de la franja (FOR UPDATE); además la base de datos
impide dos confirmaciones para la misma franja y dos reservas activas para el mismo contrato.
"""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.domain.contract_rules import ContractStatus
from app.domain.errors import ConflictError, NotFoundError, PermissionDeniedError
from app.domain.match_rules import PlaceKind
from app.domain.venue_rules import ACTIVE_BOOKINGS, BookingStatus, check_slot_covers_match
from app.persistence.models_identity import UserAccount
from app.persistence.models_venues import Booking, Court, Slot, Venue
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.contract_queries import admin_side, get_version, load_contract, terms_of

_PENDING, _CONFIRMED = BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value


def _slot(ctx: ServiceContext, slot_id: int, lock: bool = True) -> tuple[Slot, Court]:
    slot = ctx.db.get(Slot, slot_id, with_for_update=lock)
    court = ctx.db.get(Court, slot.court_id) if slot else None
    if slot is None or court is None:
        raise NotFoundError("SLOT_NOT_FOUND", "La franja no existe.")
    return slot, court


def request(ctx: ServiceContext, actor: UserAccount, contract_id: int, slot_id: int) -> Booking:
    contract = load_contract(ctx, contract_id, lock=True)
    _side, team = admin_side(ctx, contract, actor)
    if contract.status == ContractStatus.CANCELLED or contract.signed_version_id is None:
        raise ConflictError("CONTRACT_NOT_SIGNED", "Solo se reserva cancha para partidos firmados por ambos.")
    terms = terms_of(get_version(ctx, contract.signed_version_id))
    if terms.place_kind != PlaceKind.VENUE:
        raise ConflictError("PLACE_NOT_VENUE", "El contrato firmado no es en cancha de establecimiento.")
    slot, court = _slot(ctx, slot_id)
    if court.sport_code != contract.sport_code:
        raise ConflictError("COURT_WRONG_SPORT", "Esa cancha no es del deporte del partido.")
    check_slot_covers_match((slot.starts_at, slot.ends_at), terms.kickoff_at, terms.duration_minutes)
    if ctx.db.scalar(select(Booking.id).where(Booking.contract_id == contract.id,
                                              Booking.status.in_(ACTIVE_BOOKINGS))) is not None:
        raise ConflictError("BOOKING_ALREADY_ACTIVE", "Este partido ya tiene una reserva pendiente o confirmada.")
    if ctx.db.scalar(select(Booking.id).where(Booking.slot_id == slot.id, Booking.status == _CONFIRMED)):
        raise ConflictError("SLOT_TAKEN", "Esa franja ya está reservada para otro partido.")
    booking = Booking(slot_id=slot.id, contract_id=contract.id, team_id=team.id, status=_PENDING,
                      requested_by=actor.id, requested_at=ctx.clock.now())
    ctx.db.add(booking)
    ctx.db.flush()
    record_event(ctx, action="BOOKING_REQUESTED", entity="match_contract", entity_id=contract.id,
                 initiated_by=actor.id, after={"booking_id": booking.id, "slot_id": slot.id, "team_id": team.id})
    return booking


def _booking(ctx: ServiceContext, booking_id: int) -> tuple[Booking, Slot, Venue]:
    booking = ctx.db.get(Booking, booking_id)
    if booking is None:
        raise NotFoundError("BOOKING_NOT_FOUND", "La reserva no existe.")
    slot, court = _slot(ctx, booking.slot_id)  # bloquea la franja antes de releer la reserva
    ctx.db.refresh(booking)
    venue = ctx.db.get(Venue, court.venue_id)
    assert venue is not None
    return booking, slot, venue


def decide(ctx: ServiceContext, actor: UserAccount, booking_id: int, confirm: bool) -> Booking:
    booking, slot, venue = _booking(ctx, booking_id)
    if venue.owner_id != actor.id:
        raise PermissionDeniedError("VENUE_OWNER_ONLY", "Solo el dueño del establecimiento puede confirmar reservas.")
    if booking.status != _PENDING:
        raise ConflictError("BOOKING_NOT_PENDING", "Esta reserva ya fue decidida.")
    now = ctx.clock.now()
    booking.status = _CONFIRMED if confirm else BookingStatus.REJECTED.value
    booking.decided_by, booking.decided_at = actor.id, now
    if confirm:
        for other in ctx.db.scalars(select(Booking).where(Booking.slot_id == slot.id, Booking.status == _PENDING,
                                                          Booking.id != booking.id)):
            other.status, other.decided_by, other.decided_at = BookingStatus.REJECTED.value, actor.id, now
    try:
        ctx.db.flush()
    except IntegrityError as error:  # otra confirmación ganó la carrera
        raise ConflictError("SLOT_TAKEN", "Esa franja ya está reservada para otro partido.") from error
    record_event(ctx, action="BOOKING_CONFIRMED" if confirm else "BOOKING_REJECTED", entity="match_contract",
                 entity_id=booking.contract_id, initiated_by=booking.requested_by, approved_by=actor.id,
                 before={"status": _PENDING}, after={"booking_id": booking.id, "status": booking.status})
    return booking


def cancel(ctx: ServiceContext, actor: UserAccount, booking_id: int) -> Booking:
    """Un administrador de cualquiera de los dos equipos del partido cancela la reserva activa."""
    booking, _slot_row, _venue = _booking(ctx, booking_id)
    admin_side(ctx, load_contract(ctx, booking.contract_id), actor)
    return _cancel(ctx, booking, actor.id)


def _cancel(ctx: ServiceContext, booking: Booking, actor_id: int) -> Booking:
    if booking.status not in ACTIVE_BOOKINGS:
        raise ConflictError("BOOKING_CLOSED", "Esta reserva ya está cerrada.")
    before = booking.status
    booking.status, booking.decided_by, booking.decided_at = BookingStatus.CANCELLED.value, actor_id, ctx.clock.now()
    ctx.db.flush()
    record_event(ctx, action="BOOKING_CANCELLED", entity="match_contract", entity_id=booking.contract_id,
                 initiated_by=actor_id, before={"status": before}, after={"booking_id": booking.id,
                                                                          "status": booking.status})
    return booking


def cancel_for_contract(ctx: ServiceContext, contract_id: int, actor_id: int) -> None:
    """Al cancelar el partido se libera la franja reservada."""
    for booking in ctx.db.scalars(select(Booking).where(Booking.contract_id == contract_id,
                                                        Booking.status.in_(ACTIVE_BOOKINGS))):
        _cancel(ctx, booking, actor_id)

