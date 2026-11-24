"""API del Sprint 2 con catálogo SINTÉTICO [SIMULACIÓN]."""

from datetime import UTC, datetime, timedelta

from app.services import neighborhood_service
from app.services.clock import SystemClock
from app.services.context import ServiceContext
from tests.api.conftest import auth, register
from tests.conftest import CATALOG
from tests.services.test_neighborhood_service import SYNTHETIC_CSV


def seed_catalog(client) -> None:
    with client.app.state.session_factory() as session:
        ctx = ServiceContext(db=session, clock=SystemClock(), catalog=CATALOG,
                             session_ttl=timedelta(days=1), session_idle=timedelta(days=1))
        neighborhood_service.import_csv(ctx, SYNTHETIC_CSV)
        session.commit()


def team(client, token, name, barrio) -> int:
    response = client.post("/api/v1/teams", headers=auth(token), json={
        "name": name, "sport_code": "FOOTBALL", "modality_code": "F7",
        "city": "Ciudad Prueba", "neighborhood": barrio})
    assert response.status_code == 201, response.text
    return int(response.json()["team"]["id"])


def test_rivals_nearby_show_band_never_coordinates(client):
    seed_catalog(client)
    a, b = register(client, "a@r.test"), register(client, "b@r.test")
    team_a = team(client, a["token"], "Águilas", "Barrio Uno")
    team(client, b["token"], "Bravos", "Barrio Dos")
    response = client.get(f"/api/v1/teams/{team_a}/rivals", params={"scope": "NEARBY", "radius_km": 5},
                          headers=auth(a["token"]))
    assert response.status_code == 200
    body = response.json()
    assert body["items"][0]["distance_band"] == "UNDER_2_KM"
    assert "lat" not in response.text and "lon" not in response.text


def test_free_agent_invitation_flow(client):
    captain, player = register(client, "cap@r.test"), register(client, "libre@r.test")
    team_id = team(client, captain["token"], "Halcones", "Barrio Uno")
    client.post("/api/v1/me/free-agent", headers=auth(player["token"]),
                json={"sport_code": "FOOTBALL", "active": True, "position": "Arquero"})
    found = client.get("/api/v1/free-agents", params={"sport": "FOOTBALL", "city": "barranquilla"},
                       headers=auth(captain["token"])).json()
    assert found["items"][0]["position"] == "Arquero"
    invited = client.post(f"/api/v1/teams/{team_id}/invitations", headers=auth(captain["token"]),
                          json={"user_id": player["user"]["id"]})
    assert invited.status_code == 201
    invitation_id = client.get("/api/v1/me/invitations", headers=auth(player["token"])).json()[0]["id"]
    assert client.post(f"/api/v1/invitations/{invitation_id}/accept", headers=auth(captain["token"])).status_code == 404
    assert client.post(f"/api/v1/invitations/{invitation_id}/accept", headers=auth(player["token"])).status_code == 200


def test_match_request_offer_accept_flow(client):
    a, b = register(client, "a@r.test"), register(client, "b@r.test")
    team_a, team_b = team(client, a["token"], "Águilas", "Barrio Uno"), team(client, b["token"], "Bravos", "Barrio Dos")
    start = datetime.now(UTC) + timedelta(days=1)
    created = client.post(f"/api/v1/teams/{team_a}/match-requests", headers=auth(a["token"]), json={
        "window_start": start.isoformat(), "window_end": (start + timedelta(days=2)).isoformat(),
        "scope": "CITY", "referee_mode": "EITHER", "place_kind": "INFORMAL", "place_note": "Parque"})
    assert created.status_code == 201, created.text
    request_id = created.json()["id"]
    feed = client.get(f"/api/v1/teams/{team_b}/match-feed", headers=auth(b["token"])).json()
    assert [r["id"] for r in feed] == [request_id]
    offer = client.post(f"/api/v1/teams/{team_b}/match-requests/{request_id}/offers", headers=auth(b["token"]), json={
        "proposed_start": (start + timedelta(hours=5)).isoformat(), "referee_mode": "WITHOUT", "place_kind": "INFORMAL"})
    assert offer.status_code == 201, offer.text
    accepted = client.post(f"/api/v1/offers/{offer.json()['id']}/accept", headers=auth(a["token"]))
    assert accepted.json()["status"] == "ACCEPTED"
    mine = client.get(f"/api/v1/teams/{team_a}/match-requests", headers=auth(a["token"])).json()
    assert mine[0]["status"] == "MATCHED"


def test_naive_datetime_rejected(client):
    a = register(client, "a@r.test")
    team_a = team(client, a["token"], "Águilas", "Barrio Uno")
    response = client.post(f"/api/v1/teams/{team_a}/match-requests", headers=auth(a["token"]), json={
        "window_start": "2030-01-01T10:00:00", "window_end": "2030-01-02T10:00:00",
        "scope": "CITY", "referee_mode": "EITHER", "place_kind": "TO_AGREE"})
    assert response.status_code == 422


def test_search_quota_per_user(client):
    a = register(client, "a@r.test")
    team_a = team(client, a["token"], "Águilas", "Barrio Uno")
    statuses = [client.get(f"/api/v1/teams/{team_a}/rivals", headers=auth(a["token"])).status_code for _ in range(61)]
    assert statuses[:60] == [200] * 60
    assert statuses[60] == 429
