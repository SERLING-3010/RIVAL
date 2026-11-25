"""API de rivales sugeridos (Sprint 18)."""

from tests.api.conftest import auth, register
from tests.api.test_api_contracts import team


def test_suggestions_through_api(client):
    a, b, c = register(client, "a@r.test"), register(client, "b@r.test"), register(client, "c@r.test")
    mine = team(client, a["token"], "Águilas", "Barrio Uno")
    team(client, b["token"], "Bravos", "Barrio Dos")
    got = client.get(f"/api/v1/teams/{mine}/suggestions", headers=auth(a["token"]))
    assert got.status_code == 200, got.text
    for s in got.json():
        assert s["reasons"] and set(s) == {"team", "distance_band", "level", "reasons"}
    assert client.get(f"/api/v1/teams/{mine}/suggestions", headers=auth(c["token"])).status_code == 403
