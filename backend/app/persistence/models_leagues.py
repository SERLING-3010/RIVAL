"""Ligas, su personal, equipos inscritos y cuerpo arbitral (Sprint 5).

Una solicitud pendiente o aprobada por liga y equipo (o árbitro): índice único parcial.
Las rechazadas o retiradas se conservan como historial.
"""

from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base, UtcDateTime

_ACTIVE = text("status IN ('PENDING', 'APPROVED')")


class League(Base):
    __tablename__ = "league"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60))
    name_key: Mapped[str] = mapped_column(String(60), index=True)
    sport_code: Mapped[str] = mapped_column(String(30), index=True)
    modality_code: Mapped[str] = mapped_column(String(30))
    city: Mapped[str] = mapped_column(String(60))
    city_key: Mapped[str] = mapped_column(String(60), index=True)
    season: Mapped[str] = mapped_column(String(10))
    description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    created_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    # Ventana de traspasos (Sprint 13). Sin ventana, los traspasos están abiertos.
    transfer_window_start: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)
    transfer_window_end: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)


class LeagueStaff(Base):
    __tablename__ = "league_staff"
    __table_args__ = (UniqueConstraint("league_id", "user_id", name="uq_league_staff"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    league_id: Mapped[int] = mapped_column(ForeignKey("league.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), index=True)
    role: Mapped[str] = mapped_column(String(30))
    added_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    added_at: Mapped[datetime] = mapped_column(UtcDateTime)


class LeagueTeam(Base):
    __tablename__ = "league_team"
    __table_args__ = (
        Index("uq_league_team_active", "league_id", "team_id", unique=True,
              sqlite_where=_ACTIVE, postgresql_where=_ACTIVE),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    league_id: Mapped[int] = mapped_column(ForeignKey("league.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)
    status: Mapped[str] = mapped_column(String(20))
    requested_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    requested_at: Mapped[datetime] = mapped_column(UtcDateTime)
    decided_by: Mapped[int | None] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)


class LeagueReferee(Base):
    __tablename__ = "league_referee"
    __table_args__ = (
        Index("uq_league_referee_active", "league_id", "user_id", unique=True,
              sqlite_where=_ACTIVE, postgresql_where=_ACTIVE),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    league_id: Mapped[int] = mapped_column(ForeignKey("league.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), index=True)
    status: Mapped[str] = mapped_column(String(20))
    requested_at: Mapped[datetime] = mapped_column(UtcDateTime)
    decided_by: Mapped[int | None] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)
