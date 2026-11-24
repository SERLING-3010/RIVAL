"""Contrato del partido, sus versiones inmutables y las firmas (Sprint 3).

Una versión nunca se actualiza: solo se insertan filas. El contrato apunta a la versión
en curso (`current_version_id`) y a la última firmada por ambos (`signed_version_id`).
"""

from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base, UtcDateTime


class MatchContract(Base):
    __tablename__ = "match_contract"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("match_request.id"), unique=True)
    offer_id: Mapped[int] = mapped_column(ForeignKey("match_offer.id"), unique=True)
    host_team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)
    guest_team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)
    sport_code: Mapped[str] = mapped_column(String(30))
    modality_code: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(20), index=True)
    current_version_id: Mapped[int | None] = mapped_column(nullable=True)
    signed_version_id: Mapped[int | None] = mapped_column(nullable=True)
    cancel_reason: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cancelled_by: Mapped[int | None] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    updated_at: Mapped[datetime] = mapped_column(UtcDateTime)


class MatchContractVersion(Base):
    __tablename__ = "match_contract_version"
    __table_args__ = (UniqueConstraint("contract_id", "version", name="uq_contract_version"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("match_contract.id"), index=True)
    version: Mapped[int]
    terms: Mapped[dict[str, object]] = mapped_column(JSON)
    proposed_by_team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"), nullable=True)
    proposed_by: Mapped[int | None] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    note: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)


class MatchContractSignature(Base):
    __tablename__ = "match_contract_signature"
    __table_args__ = (UniqueConstraint("version_id", "team_id", name="uq_contract_signature"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    version_id: Mapped[int] = mapped_column(ForeignKey("match_contract_version.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"))
    signed_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    signed_at: Mapped[datetime] = mapped_column(UtcDateTime)
