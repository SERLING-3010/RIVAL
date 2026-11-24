"""Resultado del partido y reporte de cada equipo (Sprint 4).

Cada equipo tiene un reporte que puede corregir mientras el resultado no esté confirmado;
cada corrección queda en la auditoría con antes y después.
"""

from datetime import datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base, UtcDateTime


class MatchResult(Base):
    __tablename__ = "match_result"

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("match_contract.id"), unique=True)
    status: Mapped[str] = mapped_column(String(20), index=True)
    host_score: Mapped[int | None] = mapped_column(nullable=True)
    guest_score: Mapped[int | None] = mapped_column(nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(UtcDateTime)


class MatchResultReport(Base):
    __tablename__ = "match_result_report"
    __table_args__ = (UniqueConstraint("contract_id", "team_id", name="uq_result_report"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("match_contract.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"))
    host_score: Mapped[int]
    guest_score: Mapped[int]
    reported_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    reported_at: Mapped[datetime] = mapped_column(UtcDateTime)
