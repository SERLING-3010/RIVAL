"""API del calendario, la tabla y los árbitros de liga (Sprint 8)."""

from datetime import UTC, datetime, timedelta

from app.services.clock import FixedClock
from tests.api.conftest import auth, create_team, register
from tests.api.test_api_leagues import make_league


def league_ready(client):
    org, dt, ref = register(client, "org@r.test"), register(client, "dt@r.test"), register(client, "ref@r.test", "REFEREE")
    team_org, team_dt = create_team(client, org["token"], "Águilas"), create_team(client, dt["token"], "Bravos")
    league_id = make_league(client, org["token"]).json()["league"]["id"]
    for user, team in ((org, team_org), (dt, team_dt)):
        entry = client.post(f"/api/v1/leagues/{league_id}/team-requests", headers=auth(user["token"]),
                            json={"team_id": team}).json()["my_team_requests"][0]["id"]
        client.post(f"/api/v1/league-requests/team/{entry}/approve", headers=auth(org["token"]))
    asked = client.post(f"/api/v1/leagues/{league_id}/referee-requests", headers=auth(ref["token"])).json()
    client.post(f"/api/v1/league-requests/referee/{asked['my_referee_request']['id']}/approve", headers=auth(org["token"]))
    return org, dt, ref, league_id


def test_calendar_referee_and_table(client):
    org, dt, ref, league_id = league_ready(client)
    first = datetime.now(UTC) + timedelta(days=2)
    created = client.post(f"/api/v1/leagues/{league_id}/fixtures", headers=auth(org["token"]),
                          json={"first_kickoff": first.isoformat(), "days_between": 7})
    assert created.status_code == 201, created.text
    assert len(created.json()) == 1
    contract_id = created.json()[0]["contract_id"]
    assert client.post(f"/api/v1/leagues/{league_id}/fixtures", headers=auth(org["token"]),
                       json={"first_kickoff": first.isoformat(), "days_between": 7}).status_code == 409
    assigned = client.post(f"/api/v1/contracts/{contract_id}/referee", headers=auth(org["token"]),
                           json={"referee_id": ref["user"]["id"]})
    assert assigned.status_code == 201, assigned.text
    mine = client.get("/api/v1/me/referee-matches", headers=auth(ref["token"])).json()
    accepted = client.post(f"/api/v1/referee-assignments/{mine[0]['assignment_id']}/accept", headers=auth(ref["token"]))
    assert accepted.json()[0]["status"] == "ACCEPTED"
    for user in (org, dt):
        client.post(f"/api/v1/contracts/{contract_id}/sign", headers=auth(user["token"]), json={"version": 1})
    contract = client.get(f"/api/v1/contracts/{contract_id}", headers=auth(dt["token"])).json()
    assert (contract["league_id"], contract["request_id"], contract["referee"]["status"]) == (league_id, None, "ACCEPTED")
    client.app.state.clock = FixedClock(first + timedelta(hours=2))
    result = client.post(f"/api/v1/contracts/{contract_id}/referee-result", headers=auth(ref["token"]),
                         json={"host_score": 1, "guest_score": 0})
    assert (result.status_code, result.json()[0]["result_status"]) == (200, "CONFIRMED")
    table = client.get(f"/api/v1/leagues/{league_id}/table", headers=auth(dt["token"])).json()
    assert [r["points"] for r in table] == [3, 0]
    calendar = client.get(f"/api/v1/leagues/{league_id}/calendar", headers=auth(ref["token"])).json()
    assert calendar[0]["result"] == "1 – 0"
    denied = client.post(f"/api/v1/contracts/{contract_id}/referee-result", headers=auth(dt["token"]),
                         json={"host_score": 0, "guest_score": 5})
    assert denied.status_code == 403
