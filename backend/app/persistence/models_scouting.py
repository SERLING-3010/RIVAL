"""Perfil de agente libre: un jugador sin equipo que quiere ser encontrado para un deporte."""

from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base, UtcDateTime


class FreeAgentProfile(Base):
    __tablename__ = "free_agent_profile"
    __table_args__ = (UniqueConstraint("user_id", "sport_code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id", ondelete="CASCADE"), index=True)
    sport_code: Mapped[str] = mapped_column(String(30), index=True)
    position: Mapped[str | None] = mapped_column(String(40), nullable=True)
    note: Mapped[str | None] = mapped_column(String(200), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(UtcDateTime)
