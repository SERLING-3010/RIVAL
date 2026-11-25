"""Cartas especiales (Sprint 23): goles con tipo que confirma el rival y cartas ganadas (jugador y equipo)."""

from datetime import datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base, UtcDateTime


class GoalClaim(Base):
    """Un gol con tipo (chilena, olímpico…) marcado en la planilla. Cuenta solo si el rival lo confirma."""

    __tablename__ = "goal_claim"

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("match_contract.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), index=True)
    kind: Mapped[str] = mapped_column(String(15))
    status: Mapped[str] = mapped_column(String(12), index=True)  # PENDING, CONFIRMED, REJECTED
    claimed_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    claimed_at: Mapped[datetime] = mapped_column(UtcDateTime)
    decided_by: Mapped[int | None] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)


class SpecialCard(Base):
    """Carta especial ganada. No se borra aunque la media baje después."""

    __tablename__ = "special_card"
    __table_args__ = (UniqueConstraint("user_id", "code", name="uq_special_card"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), index=True)
    code: Mapped[str] = mapped_column(String(20))
    earned_at: Mapped[datetime] = mapped_column(UtcDateTime)


class TeamSpecialCard(Base):
    """Carta especial ganada por un equipo. No se borra aunque la media del equipo baje."""

    __tablename__ = "team_special_card"
    __table_args__ = (UniqueConstraint("team_id", "code", name="uq_team_special_card"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)
    code: Mapped[str] = mapped_column(String(20))
    earned_at: Mapped[datetime] = mapped_column(UtcDateTime)
