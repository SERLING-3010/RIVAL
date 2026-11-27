"""API del día del partido: convocatoria, valoraciones y nivel (Sprint 10)."""

from tests.api.conftest import auth
from tests.api.test_api_contracts import matched
from tests.api.test_api_results import signed_and_played


def test_callup_flow(client):
    a, _b, c, team_a, contract_id = matched(client)
    sent = client.post(f"/api/v1/contracts/{contract_id}/callup", headers=auth(a["token"]),
                       json={"user_ids": [a["user"]["id"]]})
    assert (sent.status_code, sent.json()["pending"]) == (200, 1)
    answered = client.post(f"/api/v1/contracts/{contract_id}/callup/respond", headers=auth(a["token"]),
                           json={"going": True})
    assert answered.json()["going"] == 1
    mine = client.get("/api/v1/me/callups", headers=auth(a["token"])).json()
    assert [(m["contract_id"], m["status"]) for m in mine] == [(contract_id, "GOING")]
    assert client.get(f"/api/v1/contracts/{contract_id}/callup", headers=auth(c["token"])).status_code == 404


def test_level_and_ratings_after_confirmed_match(client):
    a, b, _c, team_a, contract_id = signed_and_played(client)
    for user in (a, b):
        client.post(f"/api/v1/contracts/{contract_id}/result", headers=auth(user["token"]),
                    json={"host_score": 1, "guest_score": 0})
    manager = client.get(f"/api/v1/teams/{team_a}/manager", headers=auth(a["token"])).json()
    assert manager["level"] > 1500 and manager["level_matches"] == 1
    client.post(f"/api/v1/contracts/{contract_id}/lineup", headers=auth(a["token"]),
                json={"players": [{"user_id": a["user"]["id"], "goals": 1}]})
    assert client.get(f"/api/v1/contracts/{contract_id}/ratings/pending", headers=auth(a["token"])).json() == []
    self_rate = client.post(f"/api/v1/contracts/{contract_id}/ratings", headers=auth(a["token"]),
                            json={"rated_id": a["user"]["id"], "score": 10})
    assert (self_rate.status_code, self_rate.json()["code"]) == (422, "CANNOT_RATE_SELF")
