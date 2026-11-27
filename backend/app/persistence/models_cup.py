"""Copa eliminatoria de una liga (Sprint 16): una por liga, con su cuadro completo desde el inicio."""

from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base, UtcDateTime


class LeagueCup(Base):
    __tablename__ = "league_cup"

    id: Mapped[int] = mapped_column(primary_key=True)
    league_id: Mapped[int] = mapped_column(ForeignKey("league.id"), unique=True)
    first_kickoff: Mapped[datetime] = mapped_column(UtcDateTime)
    days_between: Mapped[int]
    rounds: Mapped[int]
    champion_team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"), nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)


class CupMatch(Base):
    """Un cruce del cuadro. Tiene contrato cuando ya se conocen sus dos equipos."""

    __tablename__ = "cup_match"
    __table_args__ = (UniqueConstraint("cup_id", "round", "position", name="uq_cup_match_slot"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    cup_id: Mapped[int] = mapped_column(ForeignKey("league_cup.id"), index=True)
    round: Mapped[int]
    position: Mapped[int]
    host_team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"), nullable=True)
    guest_team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"), nullable=True)
    contract_id: Mapped[int | None] = mapped_column(ForeignKey("match_contract.id"), nullable=True, unique=True)
    winner_team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"), nullable=True)
    tiebreak_winner_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"), nullable=True)
