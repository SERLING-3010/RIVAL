"""API del resultado y la actividad (Sprint 4)."""

from datetime import UTC, datetime, timedelta

from app.services.clock import FixedClock
from tests.api.conftest import auth
from tests.api.test_api_contracts import matched


def signed_and_played(client):
    a, b, c, team_a, contract_id = matched(client)
    for user in (a, b):
        client.post(f"/api/v1/contracts/{contract_id}/sign", headers=auth(user["token"]), json={"version": 1})
    client.app.state.clock = FixedClock(datetime.now(UTC) + timedelta(days=2))  # el partido ya se jugó
    return a, b, c, team_a, contract_id


def test_report_confirm_and_summary(client):
    a, b, _c, team_a, contract_id = signed_and_played(client)
    first = client.post(f"/api/v1/contracts/{contract_id}/result", headers=auth(a["token"]),
                        json={"host_score": 2, "guest_score": 1})
    assert first.status_code == 200, first.text
    assert (first.json()["result"]["status"], first.json()["result"]["host_score"]) == ("PENDING", None)
    second = client.post(f"/api/v1/contracts/{contract_id}/result", headers=auth(b["token"]),
                         json={"host_score": 2, "guest_score": 1})
    assert second.json()["result"]["status"] == "CONFIRMED"
    item = client.get(f"/api/v1/teams/{team_a}/contracts", headers=auth(a["token"])).json()[0]
    assert (item["result_status"], item["host_score"], item["guest_score"]) == ("CONFIRMED", 2, 1)


def test_mismatch_disputes_and_bad_scores(client):
    a, b, _c, _team_a, contract_id = signed_and_played(client)
    client.post(f"/api/v1/contracts/{contract_id}/result", headers=auth(a["token"]), json={"host_score": 2, "guest_score": 1})
    disputed = client.post(f"/api/v1/contracts/{contract_id}/result", headers=auth(b["token"]),
                           json={"host_score": 1, "guest_score": 1})
    assert disputed.json()["result"]["status"] == "DISPUTED"
    huge = client.post(f"/api/v1/contracts/{contract_id}/result", headers=auth(b["token"]),
                       json={"host_score": 1000, "guest_score": 1})
    assert (huge.status_code, huge.json()["code"]) == (422, "SCORE_OUT_OF_RANGE")


def test_activity_visibility(client):
    a, b, c, team_a, contract_id = signed_and_played(client)
    feed = client.get(f"/api/v1/contracts/{contract_id}/activity", headers=auth(b["token"]))
    assert feed.status_code == 200
    assert [e["action"] for e in feed.json()][:2] == ["CONTRACT_SIGNED", "CONTRACT_SIGNED"]
    assert feed.json()[0]["actor_name"] == "José Peña"
    assert client.get(f"/api/v1/contracts/{contract_id}/activity", headers=auth(c["token"])).status_code == 404
    assert client.get(f"/api/v1/teams/{team_a}/activity", headers=auth(c["token"])).status_code == 403
    team_feed = client.get(f"/api/v1/teams/{team_a}/activity", headers=auth(a["token"]))
    assert "TEAM_CREATED" in {e["action"] for e in team_feed.json()}
    assert "@" not in team_feed.text
