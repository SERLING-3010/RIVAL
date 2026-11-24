import pytest

from app.domain.errors import DomainError
from app.domain.geo import DistanceBand, distance_band, haversine_km, validate_coordinates, validate_radius_km


def test_haversine_zero_for_same_point():
    assert haversine_km(10.98, -74.80, 10.98, -74.80) == 0


def test_haversine_one_degree_latitude_is_about_111_km():
    assert haversine_km(10.0, -74.8, 11.0, -74.8) == pytest.approx(111.19, abs=0.1)


@pytest.mark.parametrize(
    ("km", "band"),
    [(0.0, DistanceBand.UNDER_2_KM), (1.99, DistanceBand.UNDER_2_KM), (2.0, DistanceBand.FROM_2_TO_5_KM),
     (5.0, DistanceBand.FROM_2_TO_5_KM), (5.01, DistanceBand.OVER_5_KM)],
)
def test_distance_band_boundaries(km, band):
    assert distance_band(km) == band


def test_radius_outside_limits_rejected():
    with pytest.raises(DomainError) as error:
        validate_radius_km(40)
    assert error.value.code == "INVALID_RADIUS"
    assert validate_radius_km(5) == 5


def test_invalid_coordinates_rejected():
    with pytest.raises(DomainError):
        validate_coordinates(95.0, -74.8)
