"""Moderación (Sprint 12): moderadores, reportes, sanciones con apelación y bloqueos entre equipos."""

from datetime import datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base, UtcDateTime


class Moderator(Base):
    """Se nombra solo por línea de comandos; no es un rol que alguien elija al registrarse."""

    __tablename__ = "moderator"

    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), primary_key=True)
    granted_at: Mapped[datetime] = mapped_column(UtcDateTime)


class Report(Base):
    __tablename__ = "report"

    id: Mapped[int] = mapped_column(primary_key=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), index=True)
    target_user_id: Mapped[int | None] = mapped_column(ForeignKey("user_account.id"), nullable=True, index=True)
    target_team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"), nullable=True, index=True)
    contract_id: Mapped[int | None] = mapped_column(ForeignKey("match_contract.id"), nullable=True)
    category: Mapped[str] = mapped_column(String(20))
    description: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), index=True)  # OPEN, DISMISSED, ACTIONED
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    decided_by: Mapped[int | None] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)
    decision_note: Mapped[str | None] = mapped_column(String(300), nullable=True)


class Sanction(Base):
    __tablename__ = "sanction"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), index=True)
    report_id: Mapped[int | None] = mapped_column(ForeignKey("report.id"), nullable=True)
    kind: Mapped[str] = mapped_column(String(20))
    reason: Mapped[str] = mapped_column(String(300))
    ends_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20))  # ACTIVE, REVOKED
    decided_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    appeal_text: Mapped[str | None] = mapped_column(String(500), nullable=True)
    appealed_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)
    appeal_decided_by: Mapped[int | None] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    appeal_decided_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)
    appeal_outcome: Mapped[str | None] = mapped_column(String(20), nullable=True)  # UPHELD, REVOKED


class TeamBlock(Base):
    __tablename__ = "team_block"
    __table_args__ = (UniqueConstraint("blocker_team_id", "blocked_team_id", name="uq_team_block"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    blocker_team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)
    blocked_team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
