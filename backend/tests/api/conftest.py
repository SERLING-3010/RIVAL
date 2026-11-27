from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.persistence.database import make_engine
from app.settings import Settings
from tests.conftest import TEST_DATABASE_URL, reset_schema


@pytest.fixture
def client() -> Iterator[TestClient]:
    if not TEST_DATABASE_URL.startswith("sqlite"):
        engine = make_engine(TEST_DATABASE_URL)
        reset_schema(engine)
        engine.dispose()
    app = create_app(Settings(database_url=TEST_DATABASE_URL))
    with TestClient(app) as test_client:
        yield test_client


def register(client: TestClient, email: str, role: str = "PLAYER") -> dict[str, object]:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "mi equipo juega los sábados",
            "display_name": "José Peña",
            "birth_date": "1998-05-10",
            "role": role,
            "sports": ["FOOTBALL"],
            "city": "Barranquilla",
            "neighborhood": "El Prado",
            "accept_terms": True,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def auth(token: object) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_team(client: TestClient, token: object, name: str = "Los Halcones") -> int:
    response = client.post(
        "/api/v1/teams",
        headers=auth(token),
        json={"name": name, "sport_code": "FOOTBALL", "modality_code": "F7",
              "city": "Barranquilla", "neighborhood": "El Prado"},
    )
    assert response.status_code == 201, response.text
    return int(response.json()["team"]["id"])
