"""API de ligas y cuerpo arbitral (Sprint 5)."""

from tests.api.conftest import auth, create_team, register


def make_league(client, token, **changes):
    body = {"name": "Liga del Prado", "sport_code": "FOOTBALL", "modality_code": "F7",
            "city": "Barranquilla", "season": "2026-2", **changes}
    return client.post("/api/v1/leagues", headers=auth(token), json=body)


def test_create_search_enroll_and_approve(client):
    org, dt = register(client, "org@r.test"), register(client, "dt@r.test")
    create_team(client, org["token"], "Águilas")
    team_id = create_team(client, dt["token"], "Bravos")
    created = make_league(client, org["token"])
    assert created.status_code == 201, created.text
    league_id = created.json()["league"]["id"]
    assert created.json()["my_role"] == "ORGANIZER"
    found = client.get("/api/v1/leagues", params={"sport": "FOOTBALL", "city": "barranquilla", "q": "prado"},
                       headers=auth(dt["token"])).json()
    assert [l["id"] for l in found["items"]] == [league_id]
    asked = client.post(f"/api/v1/leagues/{league_id}/team-requests", headers=auth(dt["token"]), json={"team_id": team_id})
    assert asked.status_code == 201, asked.text
    entry_id = asked.json()["my_team_requests"][0]["id"]
    assert asked.json()["pending_teams"] == []
    denied = client.post(f"/api/v1/league-requests/team/{entry_id}/approve", headers=auth(dt["token"]))
    assert denied.status_code == 403
    approved = client.post(f"/api/v1/league-requests/team/{entry_id}/approve", headers=auth(org["token"]))
    assert [t["team"]["name"] for t in approved.json()["teams"]] == ["Bravos"]
    mine = client.get("/api/v1/me/leagues", headers=auth(dt["token"])).json()
    assert [(m["league"]["id"], m["relation"]) for m in mine] == [(league_id, "TEAM")]
    # Cierre de temporada (Sprint 23): solo el organizador, y no sin partidos jugados.
    not_org = client.post(f"/api/v1/leagues/{league_id}/close-season", headers=auth(dt["token"]))
    assert not_org.status_code == 403
    empty = client.post(f"/api/v1/leagues/{league_id}/close-season", headers=auth(org["token"]))
    assert (empty.status_code, empty.json()["code"]) == (409, "NO_MATCHES_PLAYED")
    assert approved.json()["champion"] is None and approved.json()["closed_at"] is None


def test_referee_request_and_rules(client):
    org, ref, nobody = register(client, "org@r.test"), register(client, "ref@r.test", "REFEREE"), register(client, "x@r.test")
    create_team(client, org["token"])
    assert make_league(client, nobody["token"]).status_code == 403
    assert make_league(client, org["token"], season="verano").json()["code"] == "INVALID_SEASON"
    league_id = make_league(client, org["token"]).json()["league"]["id"]
    assert client.post(f"/api/v1/leagues/{league_id}/referee-requests", headers=auth(nobody["token"])).status_code == 403
    asked = client.post(f"/api/v1/leagues/{league_id}/referee-requests", headers=auth(ref["token"]))
    entry_id = asked.json()["my_referee_request"]["id"]
    staff_view = client.get(f"/api/v1/leagues/{league_id}", headers=auth(org["token"])).json()
    assert [r["id"] for r in staff_view["pending_referees"]] == [entry_id]
    client.post(f"/api/v1/league-requests/referee/{entry_id}/approve", headers=auth(org["token"]))
    public = client.get(f"/api/v1/leagues/{league_id}", headers=auth(nobody["token"])).json()
    assert ([r["display_name"] for r in public["referees"]], public["league"]["referee_count"]) == (["José Peña"], 1)
    assert "@" not in str(public)
    assert client.post(f"/api/v1/league-requests/coach/{entry_id}/approve", headers=auth(org["token"])).status_code == 422
