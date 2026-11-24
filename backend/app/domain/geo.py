"""Distancias entre centros de barrio (ADR-006). Nunca se usan posiciones de personas.

Las coordenadas son float porque no son dinero; a las personas solo se les muestra un rango.
"""

import math
from enum import StrEnum

from app.domain.errors import DomainError

EARTH_RADIUS_KM = 6371.0
MIN_RADIUS_KM = 1
MAX_RADIUS_KM = 15
DEFAULT_RADIUS_KM = 5


class DistanceBand(StrEnum):
    UNDER_2_KM = "UNDER_2_KM"
    FROM_2_TO_5_KM = "FROM_2_TO_5_KM"
    OVER_5_KM = "OVER_5_KM"


class SearchScope(StrEnum):
    NEARBY = "NEARBY"
    NEIGHBORHOOD = "NEIGHBORHOOD"
    CITY = "CITY"


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(a)))


def distance_band(km: float) -> DistanceBand:
    if km < 2:
        return DistanceBand.UNDER_2_KM
    if km <= 5:
        return DistanceBand.FROM_2_TO_5_KM
    return DistanceBand.OVER_5_KM


def validate_radius_km(radius_km: int) -> int:
    if not MIN_RADIUS_KM <= radius_km <= MAX_RADIUS_KM:
        raise DomainError(
            "INVALID_RADIUS", f"El radio debe estar entre {MIN_RADIUS_KM} y {MAX_RADIUS_KM} km."
        )
    return radius_km


def validate_coordinates(lat: float, lon: float) -> None:
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise DomainError("INVALID_COORDINATES", "Coordenadas fuera de rango.")
