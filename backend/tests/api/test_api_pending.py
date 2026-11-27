"""API de pendientes y orden por nivel (Sprint 11)."""

from tests.api.conftest import auth
from tests.api.test_api_contracts import matched


def test_pending_lists_signature_and_rivals_accept_level_order(client):
    a, b, c, team_a, contract_id = matched(client)
    pending = client.get("/api/v1/me/pending", headers=auth(a["token"])).json()
    assert [(p["kind"], p["target"], p["target_id"]) for p in pending] == [("SIGN_CONTRACT", "contract", contract_id)]
    assert pending[0]["due_at"] is not None
    assert client.get("/api/v1/me/pending", headers=auth(c["token"])).json() == []
    ordered = client.get(f"/api/v1/teams/{team_a}/rivals", params={"order": "level"}, headers=auth(a["token"]))
    assert ordered.status_code == 200 and "level" in ordered.json()["items"][0]
    bad = client.get(f"/api/v1/teams/{team_a}/rivals", params={"order": "cualquiera"}, headers=auth(a["token"]))
    assert bad.status_code == 422


def test_push_device_registration(client):
    """Sprint 24: el teléfono se registra y se quita; un token inválido se rechaza."""
    from tests.api.conftest import auth, register

    user = register(client, "push@r.test")
    token = "ExponentPushToken[telefonoDePrueba1]"
    ok = client.post("/api/v1/me/push-devices", headers=auth(user["token"]), json={"token": token})
    assert ok.status_code == 204, ok.text
    bad = client.post("/api/v1/me/push-devices", headers=auth(user["token"]), json={"token": "no-es-un-token"})
    assert (bad.status_code, bad.json()["code"]) == (422, "INVALID_PUSH_TOKEN")
    gone = client.post("/api/v1/me/push-devices/remove", headers=auth(user["token"]), json={"token": token})
    assert gone.status_code == 204
    assert client.post("/api/v1/me/push-devices", json={"token": token}).status_code == 401
