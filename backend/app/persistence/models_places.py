"""Catálogo de barrios con su punto central (ADR-006). No hay coordenadas de personas ni de equipos."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base, UtcDateTime


class Neighborhood(Base):
    __tablename__ = "neighborhood"
    __table_args__ = (UniqueConstraint("city_key", "name_key"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60))
    name_key: Mapped[str] = mapped_column(String(60))
    city: Mapped[str] = mapped_column(String(60))
    city_key: Mapped[str] = mapped_column(String(60), index=True)
    center_lat: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    center_lon: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    source: Mapped[str] = mapped_column(String(120))
    imported_at: Mapped[datetime] = mapped_column(UtcDateTime)
