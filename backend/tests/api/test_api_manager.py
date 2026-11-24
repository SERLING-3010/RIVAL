"""API del modo manager (Sprint 7)."""

from tests.api.conftest import auth, create_team, register
from tests.api.test_api_results import signed_and_played


def join_as_player(client, captain, player, team_id):
    """El jugador pide unirse y el capitán lo aprueba (flujo real del Sprint 1)."""
    asked = client.post(f"/api/v1/teams/{team_id}/join-requests", headers=auth(player["token"]), json={})
    assert asked.status_code == 201, asked.text
    requests = client.get(f"/api/v1/teams/{team_id}/join-requests", headers=auth(captain["token"])).json()
    approved = client.post(f"/api/v1/join-requests/{requests[0]['id']}/approve", headers=auth(captain["token"]))
    assert approved.status_code == 200, approved.text


def test_transfer_market_end_to_end(client):
    seller, buyer, star = register(client, "v@r.test"), register(client, "c@r.test"), register(client, "s@r.test")
    seller_team, buyer_team = create_team(client, seller["token"], "Águilas"), create_team(client, buyer["token"], "Bravos")
    join_as_player(client, seller, star, seller_team)
    star_id = star["user"]["id"]
    listed = client.post(f"/api/v1/teams/{seller_team}/transfer-list", headers=auth(seller["token"]),
                         json={"user_id": star_id, "listed": True})
    assert (listed.status_code, listed.json()["balance"]) == (200, 1000)
    market = client.get("/api/v1/market", params={"sport": "FOOTBALL", "city": "barranquilla"},
                        headers=auth(buyer["token"])).json()
    assert [m["player_id"] for m in market] == [star_id]
    offer = client.post(f"/api/v1/teams/{buyer_team}/transfer-offers", headers=auth(buyer["token"]),
                        json={"player_id": star_id, "amount": 250})
    assert offer.status_code == 201, offer.text
    offer_id = offer.json()["id"]
    early = client.post(f"/api/v1/transfer-offers/{offer_id}/player-accept", headers=auth(star["token"]))
    assert early.status_code == 403
    client.post(f"/api/v1/transfer-offers/{offer_id}/owner-accept", headers=auth(seller["token"]))
    waiting = client.get("/api/v1/me/transfer-offers", headers=auth(star["token"])).json()
    assert [(o["id"], o["to_team"]["name"]) for o in waiting] == [(offer_id, "Bravos")]
    done = client.post(f"/api/v1/transfer-offers/{offer_id}/player-accept", headers=auth(star["token"]))
    assert done.json()["status"] == "COMPLETED"
    buyer_view = client.get(f"/api/v1/teams/{buyer_team}/manager", headers=auth(buyer["token"])).json()
    assert star_id in [m["user_id"] for m in buyer_view["squad"]] and buyer_view["balance"] == 750
    card = client.get(f"/api/v1/players/{star_id}/card", headers=auth(seller["token"])).json()
    assert [t["name"] for t in card["teams"]] == ["Bravos"]
    assert "@" not in str(card)


def test_lineup_through_api(client):
    a, _b, _c, _team_a, contract_id = signed_and_played(client)
    for user in (a, _b):
        client.post(f"/api/v1/contracts/{contract_id}/result", headers=auth(user["token"]),
                    json={"host_score": 2, "guest_score": 0})
    lineup = client.post(f"/api/v1/contracts/{contract_id}/lineup", headers=auth(a["token"]),
                         json={"players": [{"user_id": a["user"]["id"], "goals": 2}]})
    assert lineup.status_code == 200, lineup.text
    card = client.get(f"/api/v1/players/{a['user']['id']}/card", headers=auth(_b["token"])).json()
    assert (card["matches"], card["goals"], card["wins"]) == (1, 2, 1)
    too_many = client.post(f"/api/v1/contracts/{contract_id}/lineup", headers=auth(a["token"]),
                           json={"players": [{"user_id": a["user"]["id"], "goals": 3}]})
    assert (too_many.status_code, too_many.json()["code"]) == (422, "GOALS_EXCEED_SCORE")
