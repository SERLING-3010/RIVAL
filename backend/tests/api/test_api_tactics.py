"""API de la alineación táctica (Sprint 19)."""

from tests.api.conftest import auth
from tests.api.test_api_contracts import matched


def test_tactics_through_api(client):
    a, b, c, _team_a, contract_id = matched(client)
    url = f"/api/v1/contracts/{contract_id}/tactics"
    mine = client.get(url, headers=auth(a["token"]))
    assert mine.status_code == 200, mine.text
    body = mine.json()
    assert (body["players_per_side"], body["uses_formation"], body["can_edit"]) == (7, True, True)
    assert "2-3-1" in body["suggested_formations"] and body["eligible"] == []
    short = client.post(url, headers=auth(a["token"]), json={"formation": "2-3-1", "starters": [], "subs": []})
    assert (short.status_code, short.json()["code"]) == (422, "STARTERS_COUNT")
    assert client.get(url, headers=auth(c["token"])).status_code == 404
    assert client.get(url, headers=auth(b["token"])).json()["team_id"] != body["team_id"]
