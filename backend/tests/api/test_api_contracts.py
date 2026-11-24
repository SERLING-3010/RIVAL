"""API del contrato de partido (Sprint 3)."""

from datetime import UTC, datetime, timedelta

from tests.api.conftest import auth, register
from tests.api.test_api_sprint2 import team


def matched(client):
    a, b, c = register(client, "a@r.test"), register(client, "b@r.test"), register(client, "c@r.test")
    team_a, team_b = team(client, a["token"], "Águilas", "Barrio Uno"), team(client, b["token"], "Bravos", "Barrio Dos")
    start = datetime.now(UTC) + timedelta(days=1)
    request_id = client.post(f"/api/v1/teams/{team_a}/match-requests", headers=auth(a["token"]), json={
        "window_start": start.isoformat(), "window_end": (start + timedelta(days=2)).isoformat(),
        "scope": "CITY", "referee_mode": "EITHER", "place_kind": "INFORMAL", "place_note": "Parque"}).json()["id"]
    offer_id = client.post(f"/api/v1/teams/{team_b}/match-requests/{request_id}/offers", headers=auth(b["token"]), json={
        "proposed_start": (start + timedelta(hours=5)).isoformat(), "referee_mode": "WITHOUT",
        "place_kind": "INFORMAL"}).json()["id"]
    accepted = client.post(f"/api/v1/offers/{offer_id}/accept", headers=auth(a["token"]))
    assert accepted.status_code == 200, accepted.text
    return a, b, c, team_a, accepted.json()["contract_id"]


def test_sign_flow_and_amendment(client):
    a, b, _c, team_a, contract_id = matched(client)
    listed = client.get(f"/api/v1/teams/{team_a}/contracts", headers=auth(a["token"])).json()
    assert [(x["id"], x["awaiting_my_signature"]) for x in listed] == [(contract_id, True)]
    detail = client.get(f"/api/v1/contracts/{contract_id}", headers=auth(b["token"])).json()
    assert (detail["my_side"], detail["status"], detail["current"]["version"]) == ("GUEST", "NEGOTIATING", 1)
    for user in (a, b):
        signed = client.post(f"/api/v1/contracts/{contract_id}/sign", headers=auth(user["token"]), json={"version": 1})
        assert signed.status_code == 200, signed.text
    assert signed.json()["status"] == "SIGNED"
    terms = {**detail["current"]["terms"], "duration_minutes": 90}
    proposal = client.post(f"/api/v1/contracts/{contract_id}/proposals", headers=auth(b["token"]),
                           json={"base_version": 1, "terms": terms, "note": "Partido largo"})
    assert proposal.status_code == 201, proposal.text
    body = proposal.json()
    assert (body["status"], body["signed"]["version"], body["current"]["signed_by"]) == ("NEGOTIATING", 1, ["GUEST"])
    stale = client.post(f"/api/v1/contracts/{contract_id}/sign", headers=auth(a["token"]), json={"version": 1})
    assert (stale.status_code, stale.json()["code"]) == (409, "CONTRACT_VERSION_CHANGED")
    rejected = client.post(f"/api/v1/contracts/{contract_id}/reject-amendment", headers=auth(a["token"]),
                           json={"version": 2})
    assert (rejected.json()["status"], rejected.json()["current"]["version"]) == ("SIGNED", 1)


def test_outsider_gets_404_and_bad_terms_get_422(client):
    a, _b, c, _team_a, contract_id = matched(client)
    assert client.get(f"/api/v1/contracts/{contract_id}", headers=auth(c["token"])).status_code == 404
    detail = client.get(f"/api/v1/contracts/{contract_id}", headers=auth(a["token"])).json()
    naive = {**detail["current"]["terms"], "kickoff_at": "2026-12-01T10:00:00"}
    response = client.post(f"/api/v1/contracts/{contract_id}/proposals", headers=auth(a["token"]),
                           json={"base_version": 1, "terms": naive})
    assert response.status_code == 422
    clash = {**detail["current"]["terms"], "guest_kit_color": "OSCURO"}
    response = client.post(f"/api/v1/contracts/{contract_id}/proposals", headers=auth(a["token"]),
                           json={"base_version": 1, "terms": clash})
    assert (response.status_code, response.json()["code"]) == (422, "KIT_COLORS_CLASH")


def test_cancel_with_reason(client):
    a, _b, _c, _team_a, contract_id = matched(client)
    response = client.post(f"/api/v1/contracts/{contract_id}/cancel", headers=auth(a["token"]),
                           json={"reason": "Lluvia fuerte anunciada"})
    assert (response.status_code, response.json()["status"]) == (200, "CANCELLED")
    assert response.json()["cancel_reason"] == "Lluvia fuerte anunciada"
