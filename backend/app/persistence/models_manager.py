"""Modo manager (Sprints 7 y 13): planilla del partido, libro de monedas RIVAL, jugadores transferibles y ofertas.

El libro de monedas solo recibe asientos nuevos (suma o resta); el saldo es la suma de los asientos.
"""

from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base, UtcDateTime

_ACTIVE = text("status IN ('PENDING_OWNER', 'PENDING_PLAYER')")
_OPEN_LOAN = text("status IN ('PENDING_OWNER', 'PENDING_PLAYER', 'ACTIVE')")


class MatchAppearance(Base):
    __tablename__ = "match_appearance"
    __table_args__ = (UniqueConstraint("contract_id", "user_id", name="uq_appearance"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("match_contract.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), index=True)
    goals: Mapped[int] = mapped_column(default=0)
    recorded_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    recorded_at: Mapped[datetime] = mapped_column(UtcDateTime)


class CoinEntry(Base):
    __tablename__ = "coin_entry"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)
    amount: Mapped[int]  # positivo = entra, negativo = sale
    reason: Mapped[str] = mapped_column(String(30))
    reference: Mapped[str | None] = mapped_column(String(60), nullable=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)


class TransferListing(Base):
    __tablename__ = "transfer_listing"
    __table_args__ = (UniqueConstraint("team_id", "user_id", name="uq_transfer_listing"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), index=True)
    listed_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    listed_at: Mapped[datetime] = mapped_column(UtcDateTime)


class TransferOffer(Base):
    __tablename__ = "transfer_offer"
    __table_args__ = (
        Index("uq_transfer_offer_active", "player_id", "to_team_id", unique=True,
              sqlite_where=_ACTIVE, postgresql_where=_ACTIVE),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), index=True)
    from_team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)
    to_team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)
    amount: Mapped[int]
    status: Mapped[str] = mapped_column(String(20), index=True)
    offered_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    owner_decided_by: Mapped[int | None] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    owner_decided_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)
    player_decided_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)


class PlayerLoan(Base):
    """Préstamo de un jugador para un solo partido (Sprint 13). No cambia de equipo ni mueve monedas."""

    __tablename__ = "player_loan"
    __table_args__ = (
        Index("uq_player_loan_open", "contract_id", "player_id", unique=True,
              sqlite_where=_OPEN_LOAN, postgresql_where=_OPEN_LOAN),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("match_contract.id"), index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), index=True)
    from_team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)
    to_team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), index=True)
    requested_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    decided_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)
