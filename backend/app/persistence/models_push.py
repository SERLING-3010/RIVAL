"""Notificaciones push (Sprint 24): teléfonos registrados y pendientes ya avisados."""

from datetime import datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base, UtcDateTime


class PushDevice(Base):
    """Un teléfono que acepta avisos. El token lo da Expo; no identifica a la persona por sí solo."""

    __tablename__ = "push_device"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), index=True)
    token: Mapped[str] = mapped_column(String(200), unique=True)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    last_seen_at: Mapped[datetime] = mapped_column(UtcDateTime)


class PushSent(Base):
    """Un pendiente que ya se avisó (o que ya existía al registrar el teléfono): no se vuelve a avisar."""

    __tablename__ = "push_sent"
    __table_args__ = (UniqueConstraint("user_id", "item_key", name="uq_push_sent"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), index=True)
    item_key: Mapped[str] = mapped_column(String(80))
    sent_at: Mapped[datetime] = mapped_column(UtcDateTime)
