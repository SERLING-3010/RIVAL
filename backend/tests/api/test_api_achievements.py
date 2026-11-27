"""API de logros e insignias (Sprint 17)."""

from tests.api.conftest import auth, create_team, register


def test_badges_through_api(client):
    a, b = register(client, "a@r.test"), register(client, "b@r.test")
    team = create_team(client, a["token"], "Águilas")
    player = client.get(f"/api/v1/players/{a['user']['id']}/badges", headers=auth(b["token"]))
    assert player.status_code == 200, player.text
    debut = next(x for x in player.json() if x["code"] == "DEBUT")
    assert (debut["earned_at"], debut["progress"]) == (None, "0/1")
    team_badges = client.get(f"/api/v1/teams/{team}/badges", headers=auth(b["token"])).json()
    assert {x["code"] for x in team_badges} >= {"FIRST_WIN", "UNBEATEN_5", "CUP_CHAMPION"}
    assert client.get("/api/v1/teams/9999/badges", headers=auth(b["token"])).status_code == 404
