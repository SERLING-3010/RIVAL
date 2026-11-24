"""Bitácora de auditoría nominal con hash encadenado (resistente a manipulación, no inmutable)."""

from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base, UtcDateTime


class AuditEvent(Base):
    __tablename__ = "audit_event"

    id: Mapped[int] = mapped_column(primary_key=True)
    chain_position: Mapped[int] = mapped_column(unique=True)
    occurred_at: Mapped[datetime] = mapped_column(UtcDateTime)
    actor_type: Mapped[str] = mapped_column(String(20))
    initiated_by: Mapped[int | None] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(60), index=True)
    entity: Mapped[str] = mapped_column(String(40), index=True)
    entity_id: Mapped[str] = mapped_column(String(40), index=True)
    before_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    after_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    correlation_id: Mapped[str] = mapped_column(String(64))
    software_version: Mapped[str] = mapped_column(String(20))
    # UNIQUE: si dos escrituras leyeran el mismo eslabón, la segunda falla en vez de bifurcar la cadena.
    prev_hash: Mapped[str] = mapped_column(String(64), unique=True)
    integrity_hash: Mapped[str] = mapped_column(String(64))


class AuditHead(Base):
    """Fila única con el último eslabón. Se bloquea (FOR UPDATE) para escribir la cadena en serie."""

    __tablename__ = "audit_head"

    id: Mapped[int] = mapped_column(primary_key=True)
    last_hash: Mapped[str] = mapped_column(String(64))
    last_position: Mapped[int] = mapped_column(default=0)
