"""Alineación táctica de cada equipo para un partido (Sprint 19). Solo la ve su propio equipo."""

from datetime import datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base, UtcDateTime


class MatchTactic(Base):
    __tablename__ = "match_tactic"
    __table_args__ = (UniqueConstraint("contract_id", "team_id", name="uq_match_tactic"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("match_contract.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"))
    formation: Mapped[str | None] = mapped_column(String(15), nullable=True)
    updated_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    updated_at: Mapped[datetime] = mapped_column(UtcDateTime)


class MatchTacticSlot(Base):
    __tablename__ = "match_tactic_slot"
    __table_args__ = (UniqueConstraint("tactic_id", "user_id", name="uq_match_tactic_slot"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tactic_id: Mapped[int] = mapped_column(ForeignKey("match_tactic.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    starter: Mapped[bool]
    sort_order: Mapped[int]
    position: Mapped[str | None] = mapped_column(String(20), nullable=True)  # solo titulares
