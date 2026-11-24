"""Solicitudes de partido (abiertas o retos directos) y ofertas de los rivales.

Una oferta nunca se edita: una contraoferta del mismo equipo crea una versión nueva
y deja la anterior como SUPERSEDED. Al aceptar una oferta la solicitud pasa a MATCHED;
el contrato con firmas llega en el Sprint 3.
"""

from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base, UtcDateTime


class MatchRequest(Base):
    __tablename__ = "match_request"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)
    target_team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"), nullable=True, index=True)
    sport_code: Mapped[str] = mapped_column(String(30))
    modality_code: Mapped[str] = mapped_column(String(30))
    scope: Mapped[str] = mapped_column(String(20))
    radius_km: Mapped[int | None] = mapped_column(nullable=True)
    window_start: Mapped[datetime] = mapped_column(UtcDateTime)
    window_end: Mapped[datetime] = mapped_column(UtcDateTime, index=True)
    referee_mode: Mapped[str] = mapped_column(String(20))
    place_kind: Mapped[str] = mapped_column(String(20))
    place_note: Mapped[str | None] = mapped_column(String(120), nullable=True)
    message: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="OPEN", index=True)
    accepted_offer_id: Mapped[int | None] = mapped_column(nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    closed_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)


class MatchOffer(Base):
    __tablename__ = "match_offer"
    __table_args__ = (
        Index(
            "uq_match_offer_pending",
            "request_id",
            "team_id",
            unique=True,
            sqlite_where=text("status = 'PENDING'"),
            postgresql_where=text("status = 'PENDING'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("match_request.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)
    version: Mapped[int] = mapped_column(default=1)
    proposed_start: Mapped[datetime] = mapped_column(UtcDateTime)
    referee_mode: Mapped[str] = mapped_column(String(20))
    place_kind: Mapped[str] = mapped_column(String(20))
    place_note: Mapped[str | None] = mapped_column(String(120), nullable=True)
    message: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    created_by: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    decided_by: Mapped[int | None] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)
