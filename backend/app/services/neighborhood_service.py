"""Catálogo de barrios: importación desde CSV y barrios dentro de un radio (ADR-006)."""

import csv
import io
from decimal import Decimal, InvalidOperation

from sqlalchemy import func, select

from app.domain.errors import DomainError
from app.domain.geo import haversine_km, validate_coordinates
from app.domain.identity_rules import validate_place_name
from app.domain.text_keys import search_key
from app.persistence.models_places import Neighborhood
from app.services.audit_service import record_event
from app.services.context import ServiceContext

EXPECTED_HEADER = ["nombre", "ciudad", "lat", "lon", "fuente"]
MAX_ROWS = 5000


def _parse_rows(text: str) -> list[tuple[str, str, Decimal, Decimal, str]]:
    reader = csv.reader(io.StringIO(text.lstrip("﻿")), delimiter=";")
    header = [h.strip().lower() for h in next(reader, [])]
    if header != EXPECTED_HEADER:
        raise DomainError("INVALID_CATALOG_FILE", f"El archivo debe empezar con: {';'.join(EXPECTED_HEADER)}")
    rows: list[tuple[str, str, Decimal, Decimal, str]] = []
    for number, raw in enumerate(reader, start=2):
        if not any(cell.strip() for cell in raw):
            continue
        if len(raw) != 5 or len(rows) >= MAX_ROWS:
            raise DomainError("INVALID_CATALOG_FILE", f"Fila {number}: se esperan 5 columnas (máximo {MAX_ROWS} filas).")
        name, city, lat_text, lon_text, source = (cell.strip() for cell in raw)
        try:
            lat, lon = Decimal(lat_text), Decimal(lon_text)
        except InvalidOperation as error:
            raise DomainError("INVALID_COORDINATES", f"Fila {number}: coordenadas no numéricas.") from error
        validate_coordinates(float(lat), float(lon))
        rows.append((validate_place_name(name, "barrio"), validate_place_name(city, "ciudad"), lat, lon, source[:120]))
    return rows


def import_csv(ctx: ServiceContext, text: str, imported_by: int | None = None) -> int:
    """Inserta o actualiza barrios por (ciudad, nombre). Devuelve cuántas filas procesó."""
    rows = _parse_rows(text)
    now = ctx.clock.now()
    for name, city, lat, lon, source in rows:
        key = (search_key(city), search_key(name))
        item = ctx.db.scalar(select(Neighborhood).where(
            Neighborhood.city_key == key[0], Neighborhood.name_key == key[1]))
        if item is None:
            item = Neighborhood(name=name, name_key=key[1], city=city, city_key=key[0])
            ctx.db.add(item)
        item.center_lat, item.center_lon = lat.quantize(Decimal("0.000001")), lon.quantize(Decimal("0.000001"))
        item.source, item.imported_at = source, now
    ctx.db.flush()
    record_event(ctx, action="NEIGHBORHOODS_IMPORTED", entity="neighborhood", entity_id="catalog",
                 initiated_by=imported_by, actor_type="HUMAN" if imported_by else "AUTOMATION",
                 after={"rows": len(rows)})
    return len(rows)


def catalog_size(ctx: ServiceContext) -> int:
    return ctx.db.scalar(select(func.count()).select_from(Neighborhood)) or 0


def center_of(ctx: ServiceContext, city: str, neighborhood: str) -> tuple[float, float] | None:
    item = ctx.db.scalar(select(Neighborhood).where(
        Neighborhood.city_key == search_key(city), Neighborhood.name_key == search_key(neighborhood)))
    return (float(item.center_lat), float(item.center_lon)) if item else None


def neighborhoods_within(ctx: ServiceContext, city: str, origin: str, radius_km: int) -> dict[str, float]:
    """Claves de barrio de la misma ciudad dentro del radio, con su distancia al barrio de origen."""
    center = center_of(ctx, city, origin)
    if center is None:
        return {}
    result: dict[str, float] = {}
    for item in ctx.db.scalars(select(Neighborhood).where(Neighborhood.city_key == search_key(city))):
        km = haversine_km(center[0], center[1], float(item.center_lat), float(item.center_lon))
        if km <= radius_km:
            result[item.name_key] = km
    return result
