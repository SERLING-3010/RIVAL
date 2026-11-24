"""Establecimientos, canchas, franjas y reservas ligadas al contrato del partido (Sprint 6).

La base de datos impide dos reservas confirmadas en la misma franja y dos reservas activas
para el mismo contrato (índices únicos parciales).
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base, UtcDateTime

_CONFIRMED = text("status = 'CONFIRMED'")
_ACTIVE = text("status IN ('PENDING', 'CONFIRMED')")


class Venue(Base):
    __tablename__ = "venue"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), index=True)
    name: Mapped[str] = mapped_column(String(60))
    name_key: Mapped[str] = mapped_column(String(60), index=True)
    address: Mapped[str] = mapped_column(String(120))
    city: Mapped[str] = mapped_column(String(60))
    city_key: Mapped[str] = mapped_column(String(60), index=True)
    neighborhood: Mapped[str] = mapped_column(String(60))
    reference_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    # Ubicación del negocio (no de personas) para el check-in (Sprint 15); la fija su dueño.
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)


class Court(Base):
    __tablename__ = "court"

    id: Mapped[int] = mapped_column(primary_key=True)
    venue_id: Mapped[int] = mapped_column(ForeignKey("venue.id"), index=True)
    name: Mapped[str] = mapped_column(String(40))
    sport_code: Mapped[str] = mapped_column(String(30))
    surface: Mapped[str | None] = mapped_column(String(40), nullable=True)


class Slot(Base):
    __tablename__ = "slot"

    id: Mapped[int] = mapped_column(primary_key=True)
    court_id: Mapped[int] = mapped_column(ForeignKey("court.id"), index=True)
    starts_at: Mapped[datetime] = mapped_column(UtcDateTime, index=True)
    ends_at: Mapped[datetime] = mapped_column(UtcDateTime)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)


class Booking(Base):
    __tablename__ = "booking"
    __table_args__ = (
        Index("uq_booking_slot_confirmed", "slot_id", unique=True,
              sqlite_where=_CONFIRMED, postgresql_where=_CONFIRMED),
        Index("uq_booking_contract_active", "contract_id", unique=True,
              sqlite_where=_ACTIVE, postgresql_where=_ACTIVE),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slot_id: Mapped[int] = mapped_column(ForeignKey("slot.id"), index=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("match_contract.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"))
    status: Mapped[str] = mapped_column(String(20))
    requested_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    requested_at: Mapped[datetime] = mapped_column(UtcDateTime)
    decided_by: Mapped[int | None] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)
