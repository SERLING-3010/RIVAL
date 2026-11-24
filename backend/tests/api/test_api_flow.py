from tests.api.conftest import auth, create_team, register


def test_catalog_is_public(client):
    response = client.get("/api/v1/catalog/sports")
    assert response.status_code == 200
    assert any(s["code"] == "FOOTBALL" for s in response.json()["sports"])


def test_register_returns_token_and_profile_without_password(client):
    body = register(client, "jugador@rival.test")
    assert body["token"]
    assert body["user"]["roles"] == ["PLAYER"]
    assert "password" not in str(body).lower()


def test_minor_rejected_with_spanish_message_and_correlation(client):
    response = client.post("/api/v1/auth/register", json={
        "email": "menor@rival.test", "password": "mi equipo juega los sábados", "display_name": "Ana",
        "birth_date": "2012-01-01", "role": "PLAYER", "sports": ["FOOTBALL"],
        "city": "Barranquilla", "neighborhood": "El Prado"})
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "UNDERAGE"
    assert "18" in body["message"]
    assert body["correlation_id"] == response.headers["X-Correlation-ID"]


def test_unknown_field_rejected(client):
    response = client.post("/api/v1/auth/register", json={"email": "x@rival.test", "is_admin": True})
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_requires_token(client):
    response = client.get("/api/v1/me")
    assert response.status_code == 401
    assert response.json()["code"] == "SESSION_EXPIRED"


def test_full_join_flow(client):
    captain = register(client, "cap@rival.test")
    player = register(client, "jug@rival.test")
    team_id = create_team(client, captain["token"])
    found = client.get("/api/v1/teams", params={"city": "barranquilla"}, headers=auth(player["token"]))
    assert found.json()["total"] == 1
    request = client.post(f"/api/v1/teams/{team_id}/join-requests", headers=auth(player["token"]), json={})
    assert request.status_code == 201
    again = client.post(f"/api/v1/teams/{team_id}/join-requests", headers=auth(player["token"]), json={})
    assert again.status_code == 409
    pending = client.get(f"/api/v1/teams/{team_id}/join-requests", headers=auth(captain["token"]))
    request_id = pending.json()[0]["id"]
    approved = client.post(f"/api/v1/join-requests/{request_id}/approve", headers=auth(captain["token"]))
    assert approved.status_code == 200
    mine = client.get("/api/v1/me/teams", headers=auth(player["token"])).json()
    assert mine[0]["team"]["name"] == "Los Halcones"
    assert mine[0]["is_admin"] is False


def test_idor_cannot_approve_other_team_request(client):
    captain_a = register(client, "a@rival.test")
    captain_b = register(client, "b@rival.test")
    player = register(client, "jug@rival.test")
    team_a = create_team(client, captain_a["token"], "Equipo A")
    create_team(client, captain_b["token"], "Equipo B")
    client.post(f"/api/v1/teams/{team_a}/join-requests", headers=auth(player["token"]), json={})
    listing = client.get(f"/api/v1/teams/{team_a}/join-requests", headers=auth(captain_b["token"]))
    assert listing.status_code == 403
    approve = client.post("/api/v1/join-requests/1/approve", headers=auth(captain_b["token"]))
    assert approve.status_code == 403


def test_team_detail_hides_private_data(client):
    captain = register(client, "cap@rival.test")
    team_id = create_team(client, captain["token"])
    detail = client.get(f"/api/v1/teams/{team_id}", headers=auth(captain["token"])).json()
    text = str(detail)
    assert "cap@rival.test" not in text
    assert "1998" not in text
    assert detail["admin_user_id"] == captain["user"]["id"]


def test_login_lockout_returns_429_with_retry_after(client):
    register(client, "jug@rival.test")
    for _ in range(5):
        client.post("/api/v1/auth/login", json={"email": "jug@rival.test", "password": "clave equivocada"})
    locked = client.post("/api/v1/auth/login", json={"email": "jug@rival.test", "password": "mi equipo juega los sábados"})
    assert locked.status_code == 429
    assert int(locked.headers["Retry-After"]) > 0


def test_logout_invalidates_session(client):
    user = register(client, "jug@rival.test")
    assert client.post("/api/v1/auth/logout", headers=auth(user["token"])).status_code == 204
    assert client.get("/api/v1/me", headers=auth(user["token"])).status_code == 401


def test_security_headers_present(client):
    response = client.get("/api/v1/catalog/sports")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Cache-Control"] == "no-store"


def test_unknown_team_returns_404(client):
    user = register(client, "jug@rival.test")
    response = client.get("/api/v1/teams/999", headers=auth(user["token"]))
    assert response.status_code == 404
    assert response.json()["code"] == "TEAM_NOT_FOUND"


def test_register_is_limited_per_ip(client):
    for i in range(10):
        register(client, f"persona{i}@rival.test")
    response = client.post("/api/v1/auth/register", json={
        "email": "once@rival.test", "password": "mi equipo juega los sábados", "display_name": "Ana",
        "birth_date": "1998-01-01", "role": "PLAYER", "sports": ["FOOTBALL"],
        "city": "Barranquilla", "neighborhood": "El Prado"})
    assert response.status_code == 429
