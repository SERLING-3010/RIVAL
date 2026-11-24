"""Check-in en la cancha (Sprint 15, ADR-004).

La app manda la posición una sola vez; aquí se compara con la de la cancha y se descarta. No se
guarda, no se registra y no va a la auditoría: solo queda "llegó" y la hora.
"""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select

from app.domain import checkin_rules
from app.domain.contract_rules import ContractStatus
from app.domain.errors import ConflictError
from app.domain.geo import haversine_km, validate_coordinates
from app.persistence.models_contracts import MatchContract
from app.persistence.models_identity import UserAccount
from app.persistence.models_matchday import MatchCheckIn
from app.persistence.models_venues import Booking, Court, Slot, Venue
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.contract_queries import get_version, terms_of
from app.services.match_participants import participant_contract

_UNAVAILABLE = {
    "CONTRACT_CANCELLED": "Este partido fue cancelado.",
    "NO_CONFIRMED_VENUE": "Solo hay check-in en partidos con cancha reservada y confirmada.",
    "NO_VENUE_LOCATION": "La cancha todavía no guardó su ubicación.",
}


@dataclass(frozen=True)
class CheckInItem:
    user_id: int
    display_name: str
    checked_in_at: datetime


@dataclass(frozen=True)
class CheckInBoardView:
    contract_id: int
    unavailable: str | None  # motivo por el que no hay check-in, o None
    venue_name: str | None
    opens_at: datetime
    closes_at: datetime
    window_open: bool
    me_checked_in: bool
    items: list[CheckInItem]


def _venue(ctx: ServiceContext, contract: MatchContract) -> tuple[Venue | None, str | None]:
    if contract.status == ContractStatus.CANCELLED:
        return None, "CONTRACT_CANCELLED"
    venue = ctx.db.scalar(select(Venue).join(Court, Court.venue_id == Venue.id).join(Slot, Slot.court_id == Court.id)
                          .join(Booking, Booking.slot_id == Slot.id)
                          .where(Booking.contract_id == contract.id, Booking.status == "CONFIRMED"))
    if venue is None:
        return None, "NO_CONFIRMED_VENUE"
    if venue.latitude is None or venue.longitude is None:
        return venue, "NO_VENUE_LOCATION"
    return venue, None


def _times(ctx: ServiceContext, contract: MatchContract) -> tuple[datetime, int]:
    terms = terms_of(get_version(ctx, contract.signed_version_id or contract.current_version_id))
    return terms.kickoff_at, terms.duration_minutes


def board(ctx: ServiceContext, actor: UserAccount, contract_id: int) -> CheckInBoardView:
    contract = participant_contract(ctx, actor, contract_id)
    venue, reason = _venue(ctx, contract)
    kickoff, minutes = _times(ctx, contract)
    rows = ctx.db.execute(select(MatchCheckIn, UserAccount.display_name)
                          .join(UserAccount, UserAccount.id == MatchCheckIn.user_id)
                          .where(MatchCheckIn.contract_id == contract.id).order_by(MatchCheckIn.checked_in_at))
    items = [CheckInItem(user_id=c.user_id, display_name=name, checked_in_at=c.checked_in_at) for c, name in rows]
    return CheckInBoardView(
        contract_id=contract.id, unavailable=_UNAVAILABLE[reason] if reason else None,
        venue_name=venue.name if venue else None, opens_at=kickoff - checkin_rules.OPENS_BEFORE_KICKOFF,
        closes_at=checkin_rules.closes_at(kickoff, minutes),
        window_open=checkin_rules.window_open(kickoff, minutes, ctx.clock.now()),
        me_checked_in=any(i.user_id == actor.id for i in items), items=items)


def check_in(ctx: ServiceContext, actor: UserAccount, contract_id: int, latitude: float,
             longitude: float) -> MatchCheckIn:
    contract = participant_contract(ctx, actor, contract_id, lock=True)
    existing = ctx.db.scalar(select(MatchCheckIn).where(MatchCheckIn.contract_id == contract.id,
                                                        MatchCheckIn.user_id == actor.id))
    if existing is not None:
        return existing  # repetir no cambia la hora de llegada
    venue, reason = _venue(ctx, contract)
    if reason is not None:
        raise ConflictError(reason, _UNAVAILABLE[reason])
    kickoff, minutes = _times(ctx, contract)
    checkin_rules.check_window(kickoff, minutes, ctx.clock.now())
    validate_coordinates(latitude, longitude)
    assert venue is not None and venue.latitude is not None and venue.longitude is not None
    checkin_rules.check_arrived(haversine_km(latitude, longitude, venue.latitude, venue.longitude))
    record = MatchCheckIn(contract_id=contract.id, user_id=actor.id, checked_in_at=ctx.clock.now())
    ctx.db.add(record)
    ctx.db.flush()
    record_event(ctx, action="CHECKED_IN", entity="match_contract", entity_id=contract.id, initiated_by=actor.id,
                 after={"user_id": actor.id})  # sin coordenadas, a propósito
    return record
