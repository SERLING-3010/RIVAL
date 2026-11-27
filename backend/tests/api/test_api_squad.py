"""API de la plantilla en modo juego (Sprint 22)."""

from tests.api.conftest import auth
from tests.api.test_api_contracts import matched


def test_squad_through_api(client):
    a, b, _c, team_a, _contract_id = matched(client)
    got = client.get(f"/api/v1/teams/{team_a}/squad", headers=auth(a["token"]))
    assert got.status_code == 200, got.text
    body = got.json()
    assert (body["suggested"], body["players_per_side"], len(body["members"])) == (True, 7, 1)
    first = body["members"][0]
    assert (first["media"], first["tier"], first["goals"], first["wins"]) == (57, "BRONCE", 0, 0)
    assert (first["rating_average"], first["hat_tricks"], first["badges"]) == (None, 0, 0)
    team_card = body["card"]  # Sprint 23: la lámina de la barra del equipo
    assert (team_card["tier"], team_card["display_tier"], len(team_card["specials"])) == ("BRONCE", "BRONCE", 15)
    assert (body["crest"], body["can_edit"], team_card["available"]) == (None, True, ["BASIC"])
    crest = client.post(f"/api/v1/teams/{team_a}/crest", headers=auth(a["token"]),
                        json={"crest": "CIRCULO|#C0182F|#FFFFFF|RAYO"})
    assert (crest.status_code, crest.json()["crest"]) == (200, "CIRCULO|#C0182F|#FFFFFF|RAYO")
    bad = client.post(f"/api/v1/teams/{team_a}/card-choice", headers=auth(a["token"]), json={"choice": "ELITE"})
    assert (bad.status_code, bad.json()["code"]) == (422, "DESIGN_NOT_OWNED")
    assert client.get(f"/api/v1/teams/{team_a}/squad", headers=auth(b["token"])).status_code == 403
    card = client.get(f"/api/v1/players/{a['user']['id']}/card", headers=auth(b["token"])).json()
    assert card["card"]["check_ins"] == 0
