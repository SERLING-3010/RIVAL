"""Catálogo de barrios. Coordenadas SINTÉTICAS [SIMULACIÓN]: no son las reales de Barranquilla."""

import pytest

from app.domain.errors import DomainError
from app.services import neighborhood_service

SYNTHETIC_CSV = """nombre;ciudad;lat;lon;fuente
Barrio Uno;Ciudad Prueba;10.000000;-74.800000;sintetico
Barrio Dos;Ciudad Prueba;10.010000;-74.800000;sintetico
Barrio Tres;Ciudad Prueba;10.040000;-74.800000;sintetico
Barrio Lejano;Ciudad Prueba;10.200000;-74.800000;sintetico
Barrio Uno;Otra Ciudad;10.000000;-74.800000;sintetico
"""


def test_import_counts_rows_and_is_idempotent(ctx):
    assert neighborhood_service.import_csv(ctx, SYNTHETIC_CSV) == 5
    assert neighborhood_service.import_csv(ctx, SYNTHETIC_CSV) == 5
    assert neighborhood_service.catalog_size(ctx) == 5


def test_import_rejects_bad_coordinates(ctx):
    with pytest.raises(DomainError) as error:
        neighborhood_service.import_csv(ctx, "nombre;ciudad;lat;lon;fuente\nMalo;X;99;-74;s\n")
    assert error.value.code == "INVALID_COORDINATES"


def test_import_rejects_wrong_header(ctx):
    with pytest.raises(DomainError) as error:
        neighborhood_service.import_csv(ctx, "a,b,c\n1,2,3\n")
    assert error.value.code == "INVALID_CATALOG_FILE"


def test_neighborhoods_within_radius_same_city_only(ctx):
    neighborhood_service.import_csv(ctx, SYNTHETIC_CSV)
    found = neighborhood_service.neighborhoods_within(ctx, "Ciudad Prueba", "barrio uno", radius_km=5)
    assert set(found) == {"barrio uno", "barrio dos", "barrio tres"}
    assert found["barrio dos"] == pytest.approx(1.11, abs=0.05)


def test_unknown_origin_has_no_center(ctx):
    neighborhood_service.import_csv(ctx, SYNTHETIC_CSV)
    assert neighborhood_service.center_of(ctx, "Ciudad Prueba", "Sin Catalogo") is None
