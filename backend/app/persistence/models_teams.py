"""Tablas de equipos, membresías y solicitudes de unión."""

from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.persistence.database import Base, UtcDateTime


class Team(Base):
    __tablename__ = "team"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60))
    name_key: Mapped[str] = mapped_column(String(60), index=True)
    sport_code: Mapped[str] = mapped_column(String(30), index=True)
    modality_code: Mapped[str] = mapped_column(String(30))
    city: Mapped[str] = mapped_column(String(60))
    city_key: Mapped[str] = mapped_column(String(60), index=True)
    neighborhood: Mapped[str] = mapped_column(String(60))
    neighborhood_key: Mapped[str] = mapped_column(String(60), index=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    created_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    # Sprint 23: escudo armado con piezas de RIVAL y diseño elegido para el cuadro de la media.
    crest: Mapped[str | None] = mapped_column(String(40), nullable=True)
    card_choice: Mapped[str | None] = mapped_column(String(20), nullable=True)

    memberships: Mapped[list["TeamMembership"]] = relationship(
        back_populates="team", cascade="all, delete-orphan", lazy="selectin", order_by="TeamMembership.id"
    )


def _one_per_team(name: str, role: str) -> Index:
    """Índice único parcial: como máximo un DT y un capitán por equipo, garantizado por la base."""
    condition = text(f"role = '{role}'")
    return Index(name, "team_id", unique=True, sqlite_where=condition, postgresql_where=condition)


class TeamMembership(Base):
    __tablename__ = "team_membership"
    __table_args__ = (
        UniqueConstraint("team_id", "user_id"),
        _one_per_team("uq_team_one_coach", "COACH"),
        _one_per_team("uq_team_one_captain", "CAPTAIN"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), index=True)
    role: Mapped[str] = mapped_column(String(20))
    joined_at: Mapped[datetime] = mapped_column(UtcDateTime)

    team: Mapped[Team] = relationship(back_populates="memberships")


class JoinRequest(Base):
    __tablename__ = "join_request"
    __table_args__ = (
        Index(
            "uq_join_request_pending",
            "team_id",
            "user_id",
            unique=True,
            sqlite_where=text("status = 'PENDING'"),
            postgresql_where=text("status = 'PENDING'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), index=True)
    desired_role: Mapped[str] = mapped_column(String(20))
    # REQUEST: el jugador pide entrar. INVITE: el equipo invita a un agente libre.
    direction: Mapped[str] = mapped_column(String(10), default="REQUEST")
    initiated_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    message: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    decided_by: Mapped[int | None] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)
