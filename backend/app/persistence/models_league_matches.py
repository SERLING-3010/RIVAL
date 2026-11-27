"""Partidos del calendario de una liga y árbitros asignados a partidos (Sprint 8)."""

from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base, UtcDateTime

_ACTIVE = text("status IN ('PENDING', 'ACCEPTED')")


class LeagueFixture(Base):
    __tablename__ = "league_fixture"

    id: Mapped[int] = mapped_column(primary_key=True)
    league_id: Mapped[int] = mapped_column(ForeignKey("league.id"), index=True)
    round: Mapped[int]
    contract_id: Mapped[int] = mapped_column(ForeignKey("match_contract.id"), unique=True)
    host_team_id: Mapped[int] = mapped_column(ForeignKey("team.id"))
    guest_team_id: Mapped[int] = mapped_column(ForeignKey("team.id"))


class RefereeAssignment(Base):
    __tablename__ = "referee_assignment"
    __table_args__ = (
        Index("uq_referee_assignment_active", "contract_id", unique=True,
              sqlite_where=_ACTIVE, postgresql_where=_ACTIVE),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("match_contract.id"), index=True)
    referee_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), index=True)
    status: Mapped[str] = mapped_column(String(20))  # PENDING, ACCEPTED, DECLINED, CANCELLED
    assigned_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    assigned_at: Mapped[datetime] = mapped_column(UtcDateTime)
    decided_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)
