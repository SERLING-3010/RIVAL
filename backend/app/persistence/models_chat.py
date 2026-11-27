"""Chat del partido (Sprint 14): mensajes de los participantes de un contrato."""

from datetime import datetime

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base, UtcDateTime


class MatchChatMessage(Base):
    __tablename__ = "match_chat_message"
    __table_args__ = (Index("ix_match_chat_contract_id_id", "contract_id", "id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("match_contract.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), index=True)
    body: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    deleted_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)
