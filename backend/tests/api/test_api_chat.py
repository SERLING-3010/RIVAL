"""API del chat del partido (Sprint 14)."""

from tests.api.conftest import auth, register
from tests.api.test_api_contracts import matched


def test_chat_flow_through_api(client):
    a, b, c, _team_a, contract_id = matched(client)
    url = f"/api/v1/contracts/{contract_id}/chat"
    sent = client.post(url, headers=auth(a["token"]), json={"text": "Nos vemos a las 6"})
    assert sent.status_code == 201, sent.text
    assert (sent.json()["body"], sent.json()["mine"]) == ("Nos vemos a las 6", True)
    client.post(url, headers=auth(b["token"]), json={"text": "Listo"})
    page = client.get(url, headers=auth(b["token"])).json()
    assert page["writable"] and [m["body"] for m in page["messages"]] == ["Nos vemos a las 6", "Listo"]
    newer = client.get(url, headers=auth(b["token"]), params={"after_id": sent.json()["id"]}).json()
    assert [m["body"] for m in newer["messages"]] == ["Listo"]
    outsider = register(client, "fuera@r.test")
    for who in (c, outsider):  # quien no juega este partido no ve el chat
        assert client.get(url, headers=auth(who["token"])).status_code == 404
    assert client.post(f"/api/v1/chat/{sent.json()['id']}/delete", headers=auth(b["token"])).status_code == 403
    assert client.post(f"/api/v1/chat/{sent.json()['id']}/delete", headers=auth(a["token"])).status_code == 200
    first = client.get(url, headers=auth(b["token"])).json()["messages"][0]
    assert (first["deleted"], first["body"]) == (True, None)
    blank = client.post(url, headers=auth(a["token"]), json={"text": "   "})
    assert (blank.status_code, blank.json()["code"]) == (422, "INVALID_MESSAGE")
    not_mod = client.get(f"/api/v1/moderation/contracts/{contract_id}/chat", headers=auth(a["token"]))
    assert not_mod.status_code == 403
