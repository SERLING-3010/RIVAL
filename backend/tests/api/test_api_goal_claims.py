"""API de goles con tipo (Sprint 23): la planilla los marca y el rival los confirma."""

from tests.api.conftest import auth
from tests.api.test_api_results import signed_and_played


def test_goal_kind_marked_in_lineup_and_confirmed_by_rival(client):
    a, b, _c, _team_a, contract_id = signed_and_played(client)
    for user in (a, b):
        client.post(f"/api/v1/contracts/{contract_id}/result", headers=auth(user["token"]),
                    json={"host_score": 2, "guest_score": 0})
    lineup = client.post(f"/api/v1/contracts/{contract_id}/lineup", headers=auth(a["token"]),
                         json={"players": [{"user_id": a["user"]["id"], "goals": 2, "kinds": ["CHILENA"]}]})
    assert lineup.status_code == 200, lineup.text
    bad = client.post(f"/api/v1/contracts/{contract_id}/lineup", headers=auth(a["token"]),
                      json={"players": [{"user_id": a["user"]["id"], "goals": 2, "kinds": ["TACON"]}]})
    assert (bad.status_code, bad.json()["code"]) == (422, "INVALID_GOAL_KIND")
    claims = client.get(f"/api/v1/contracts/{contract_id}/goal-claims", headers=auth(b["token"])).json()
    assert [(c["kind"], c["status"], c["can_decide"]) for c in claims] == [("CHILENA", "PENDING", True)]
    own = client.post(f"/api/v1/goal-claims/{claims[0]['id']}/decision", headers=auth(a["token"]),
                      json={"accept": True})
    assert (own.status_code, own.json()["code"]) == (403, "RIVAL_ONLY")
    done = client.post(f"/api/v1/goal-claims/{claims[0]['id']}/decision", headers=auth(b["token"]),
                       json={"accept": True})
    assert done.json() == {"status": "CONFIRMED"}
    card = client.get(f"/api/v1/players/{a['user']['id']}/card", headers=auth(b["token"])).json()["card"]
    assert (card["tier"], len(card["specials"]), card["display_tier"]) == ("PLATA", 15, "PLATA")
    alejandrita = next(s for s in card["specials"] if s["code"] == "ALEJANDRITA")
    assert alejandrita["goals"] == [{"label": "Gol de chilena", "current": 1, "target": 1}]
    assert alejandrita["earned_at"] is None  # tiene la chilena, pero no la media 80
