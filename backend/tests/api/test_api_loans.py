"""API de préstamos y ventanas de traspasos (Sprint 13)."""

from datetime import UTC, datetime, timedelta

from tests.api.conftest import auth, create_team, register
from tests.api.test_api_contracts import matched
from tests.api.test_api_leagues import make_league
from tests.api.test_api_manager import join_as_player


def test_loan_flow_through_api(client):
    a, _b, c, _team_a, contract_id = matched(client)
    team_c = create_team(client, c["token"], "Cóndores")
    loaned = register(client, "prestado@r.test")
    join_as_player(client, c, loaned, team_c)
    asked = client.post(f"/api/v1/contracts/{contract_id}/loans", headers=auth(a["token"]),
                        json={"player_id": loaned["user"]["id"], "from_team_id": team_c})
    assert asked.status_code == 201, asked.text
    loan_id = asked.json()[0]["id"]
    pending = client.get("/api/v1/me/pending", headers=auth(c["token"])).json()
    assert ("LOAN_OWNER", "loans") in [(p["kind"], p["target"]) for p in pending]
    owner = client.post(f"/api/v1/loans/{loan_id}/owner-accept", headers=auth(c["token"]))
    assert owner.json()["status"] == "PENDING_PLAYER"
    assert [l["id"] for l in client.get("/api/v1/me/loans", headers=auth(loaned["token"])).json()] == [loan_id]
    done = client.post(f"/api/v1/loans/{loan_id}/player-accept", headers=auth(loaned["token"]))
    assert done.json()["status"] == "ACTIVE"


def test_transfer_window_on_league(client):
    org = register(client, "org@r.test")
    create_team(client, org["token"])
    league_id = make_league(client, org["token"]).json()["league"]["id"]
    start = datetime.now(UTC) + timedelta(days=1)
    window = client.post(f"/api/v1/leagues/{league_id}/transfer-window", headers=auth(org["token"]),
                         json={"starts_at": start.isoformat(), "ends_at": (start + timedelta(days=7)).isoformat()})
    assert window.status_code == 200, window.text
    detail = client.get(f"/api/v1/leagues/{league_id}", headers=auth(org["token"])).json()
    assert detail["transfer_window_start"] is not None
    inverted = client.post(f"/api/v1/leagues/{league_id}/transfer-window", headers=auth(org["token"]),
                           json={"starts_at": start.isoformat(), "ends_at": start.isoformat()})
    assert (inverted.status_code, inverted.json()["code"]) == (422, "WINDOW_INVERTED")
