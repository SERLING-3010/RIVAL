"""Lanzamiento solo con fútbol, sin árbitros ni establecimientos (Sprint 29)."""

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.domain.launch_rules import Features, default_referee
from app.domain.match_rules import RefereeMode
from app.main import create_app
from app.persistence.database import make_engine
from app.settings import Settings
from tests.api.conftest import auth, create_team, register
from tests.conftest import TEST_DATABASE_URL, reset_schema


@pytest.fixture
def launch() -> Iterator[TestClient]:
    if not TEST_DATABASE_URL.startswith("sqlite"):
        engine = make_engine(TEST_DATABASE_URL)
        reset_schema(engine)
        engine.dispose()
    settings = Settings(database_url=TEST_DATABASE_URL, sports=("FOOTBALL",), referees=False, venues=False)
    with TestClient(create_app(settings)) as test_client:
        yield test_client


def test_only_football_players_and_coaches(launch):
    assert launch.get("/api/v1/features").json() == {"sports": ["FOOTBALL"], "referees": False, "venues": False}
    assert [s["code"] for s in launch.get("/api/v1/catalog/sports").json()["sports"]] == ["FOOTBALL"]
    referee = launch.post("/api/v1/auth/register", json={
        "email": "arbitro@r.test", "password": "mi equipo juega los sábados", "display_name": "Ana",
        "birth_date": "1990-01-01", "role": "REFEREE", "sports": ["FOOTBALL"], "city": "Barranquilla",
        "neighborhood": "El Prado", "accept_terms": True})
    assert (referee.status_code, referee.json()["code"]) == (422, "ROLE_NOT_AVAILABLE")
    player = register(launch, "jugador@r.test")
    basket = launch.post("/api/v1/teams", headers=auth(player["token"]), json={
        "name": "Aros", "sport_code": "BASKETBALL", "modality_code": "5X5", "city": "Barranquilla",
        "neighborhood": "El Prado"})
    assert basket.status_code == 422  # el baloncesto no está en este lanzamiento


def test_referee_and_venue_routes_are_off(launch):
    user = register(launch, "dt@r.test")
    for path in ("/api/v1/me/venues", "/api/v1/me/referee-matches"):
        response = launch.get(path, headers=auth(user["token"]))
        assert (response.status_code, response.json()["code"]) == (404, "FEATURE_DISABLED")


def test_matches_are_without_referee_and_never_at_a_venue(launch):
    user = register(launch, "a@r.test")
    team_id = create_team(launch, user["token"], "Águilas")
    start = datetime.now(UTC) + timedelta(days=1)
    body = {"window_start": start.isoformat(), "window_end": (start + timedelta(days=2)).isoformat(),
            "scope": "CITY", "place_kind": "INFORMAL", "place_note": "Parque"}
    url = f"/api/v1/teams/{team_id}/match-requests"
    with_ref = launch.post(url, headers=auth(user["token"]), json={**body, "referee_mode": "WITH"})
    assert (with_ref.status_code, with_ref.json()["code"]) == (422, "REFEREES_NOT_AVAILABLE")
    venue = launch.post(url, headers=auth(user["token"]), json={**body, "referee_mode": "WITHOUT",
                                                                 "place_kind": "VENUE"})
    assert (venue.status_code, venue.json()["code"]) == (422, "VENUES_NOT_AVAILABLE")
    either = launch.post(url, headers=auth(user["token"]), json={**body, "referee_mode": "EITHER"})
    assert (either.status_code, either.json()["referee_mode"]) == (201, "WITHOUT")  # «da igual» → sin árbitro


def test_league_and_cup_matches_default_to_no_referee():
    assert default_referee(Features(referees=False)) == RefereeMode.WITHOUT
    assert default_referee(Features()) == RefereeMode.WITH
