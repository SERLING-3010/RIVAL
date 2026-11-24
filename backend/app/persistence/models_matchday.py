"""Día del partido (Sprint 10): nivel Glicko-2 del equipo, convocatoria y valoraciones."""

from datetime import datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base, UtcDateTime


class TeamRating(Base):
    __tablename__ = "team_rating"

    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), primary_key=True)
    rating: Mapped[float]
    rd: Mapped[float]
    volatility: Mapped[float]
    matches: Mapped[int] = mapped_column(default=0)
    updated_at: Mapped[datetime] = mapped_column(UtcDateTime)


class CallUp(Base):
    __tablename__ = "call_up"
    __table_args__ = (UniqueConstraint("contract_id", "user_id", name="uq_call_up"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("match_contract.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), index=True)
    status: Mapped[str] = mapped_column(String(20))
    invited_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    invited_at: Mapped[datetime] = mapped_column(UtcDateTime)
    responded_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)


class PlayerRating(Base):
    __tablename__ = "player_rating"
    __table_args__ = (UniqueConstraint("contract_id", "rater_id", "rated_id", name="uq_player_rating"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("match_contract.id"), index=True)
    rater_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    rated_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), index=True)
    score: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
