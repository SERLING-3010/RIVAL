"""API de la copa eliminatoria (Sprint 16)."""

from datetime import UTC, datetime, timedelta

from tests.api.conftest import auth
from tests.api.test_api_league_matches import league_ready


def test_cup_through_api(client):
    org, dt, _ref, league_id = league_ready(client)
    url = f"/api/v1/leagues/{league_id}/cup"
    assert client.get(url, headers=auth(dt["token"])).status_code == 404
    body = {"first_kickoff": (datetime.now(UTC) + timedelta(days=2)).isoformat(), "days_between": 7}
    assert client.post(url, headers=auth(dt["token"]), json=body).status_code == 403
    created = client.post(url, headers=auth(org["token"]), json=body)
    assert created.status_code == 201, created.text
    cup = created.json()
    assert (cup["can_manage"], [r["name"] for r in cup["rounds"]]) == (True, ["Final"])
    final = cup["rounds"][0]["matches"][0]
    assert {final["host_name"], final["guest_name"]} == {"Águilas", "Bravos"} and final["contract_id"]
    seen = client.get(url, headers=auth(dt["token"])).json()
    assert seen["can_manage"] is False and seen["champion_name"] is None
    assert client.post(url, headers=auth(org["token"]), json=body).status_code == 409
    early = client.post(f"/api/v1/cup-matches/{final['id']}/tiebreak", headers=auth(org["token"]),
                        json={"winner_team_id": 1})
    assert (early.status_code, early.json()["code"]) == (409, "NO_TIE_TO_BREAK")
