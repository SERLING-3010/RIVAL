"""Búsqueda de rivales por cercanía, barrio o ciudad, con catálogo SINTÉTICO [SIMULACIÓN]."""

import pytest

from app.domain.errors import DomainError, PermissionDeniedError
from app.domain.geo import DistanceBand, SearchScope
from app.services import neighborhood_service, rival_service, team_service
from app.services.inputs import CreateTeamInput
from tests.services.test_neighborhood_service import SYNTHETIC_CSV
from tests.services.test_team_service import new_user


def make_team(ctx, email, name, barrio, modality="F7", sport="FOOTBALL"):
    owner = new_user(ctx, email)
    team = team_service.create_team(ctx, owner, CreateTeamInput(
        name=name, sport_code=sport, modality_code=modality, city="Ciudad Prueba", neighborhood=barrio))
    return owner, team


@pytest.fixture
def league(ctx):
    neighborhood_service.import_csv(ctx, SYNTHETIC_CSV)
    teams = {
        "a": make_team(ctx, "a@r.test", "Águilas", "Barrio Uno"),
        "b": make_team(ctx, "b@r.test", "Bravos", "Barrio Dos"),
        "c": make_team(ctx, "c@r.test", "Cóndores", "Barrio Lejano"),
        "d": make_team(ctx, "d@r.test", "Delfines", "Barrio Uno", modality="B5X5", sport="BASKETBALL"),
        "e": make_team(ctx, "e@r.test", "Escorpiones", "Barrio Uno", modality="F11"),
        "f": make_team(ctx, "f@r.test", "Fénix", "Barrio Uno"),
    }
    return teams


def names(page):
    return [r.team.name for r in page.items]


def test_nearby_returns_close_teams_with_band_only(ctx, league):
    owner, team = league["a"]
    page = rival_service.search_rivals(ctx, owner, team.id, SearchScope.NEARBY, radius_km=5)
    assert names(page) == ["Fénix", "Bravos"]
    assert [r.distance_band for r in page.items] == [DistanceBand.UNDER_2_KM, DistanceBand.UNDER_2_KM]


def test_neighborhood_scope_same_barrio(ctx, league):
    owner, team = league["a"]
    assert names(rival_service.search_rivals(ctx, owner, team.id, SearchScope.NEIGHBORHOOD)) == ["Fénix"]


def test_city_scope_excludes_other_sport_modality_and_self(ctx, league):
    owner, team = league["a"]
    page = rival_service.search_rivals(ctx, owner, team.id, SearchScope.CITY)
    assert names(page) == ["Bravos", "Cóndores", "Fénix"]
    assert page.total == 3


def test_nearby_without_catalog_center_explains(ctx, league):
    owner, team = make_team(ctx, "x@r.test", "Sin Mapa", "Barrio Nuevo")
    with pytest.raises(DomainError) as error:
        rival_service.search_rivals(ctx, owner, team.id, SearchScope.NEARBY, radius_km=5)
    assert error.value.code == "NEIGHBORHOOD_NOT_IN_CATALOG"


def test_only_members_search_as_team(ctx, league):
    _, team = league["a"]
    outsider = new_user(ctx, "out@r.test")
    with pytest.raises(PermissionDeniedError):
        rival_service.search_rivals(ctx, outsider, team.id, SearchScope.CITY)
