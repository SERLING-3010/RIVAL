"""Mis datos (Sprint 27): términos, descargar mis datos y eliminar la cuenta (Ley 1581)."""

from tests.api.conftest import auth, create_team, register

PASSWORD = "mi equipo juega los sábados"
BASE = {"password": PASSWORD, "display_name": "Ana", "birth_date": "1998-01-01", "role": "PLAYER",
        "sports": ["FOOTBALL"], "city": "Barranquilla", "neighborhood": "El Prado"}


def test_terms_are_required_and_versioned(client):
    refused = client.post("/api/v1/auth/register", json={**BASE, "email": "sin@rival.test"})
    assert (refused.status_code, refused.json()["code"]) == (422, "TERMS_NOT_ACCEPTED")
    user = register(client, "con@rival.test")
    assert user["user"]["needs_terms"] is False
    version = client.get("/api/v1/legal/terms-version").json()["version"]
    old = client.post("/api/v1/me/accept-terms", headers=auth(user["token"]), json={"version": "2020-01-01"})
    assert (old.status_code, old.json()["code"]) == (422, "TERMS_VERSION_OUTDATED")
    ok = client.post("/api/v1/me/accept-terms", headers=auth(user["token"]), json={"version": version})
    assert (ok.status_code, ok.json()["needs_terms"]) == (200, False)


def test_data_export_contains_only_my_data(client):
    user = register(client, "datos@rival.test")
    create_team(client, user["token"], "Águilas")
    data = client.get("/api/v1/me/data-export", headers=auth(user["token"])).json()
    assert data["perfil"]["correo"] == "datos@rival.test"
    assert [t["equipo"] for t in data["equipos"]] == ["Águilas"]
    assert data["aceptacion_terminos"]["version"] is not None
    assert set(data) >= {"partidos", "valoraciones_recibidas", "mensajes_de_chat", "check_ins"}


def test_delete_account_anonymizes_and_frees_the_email(client):
    user = register(client, "borrar@rival.test")
    team_id = create_team(client, user["token"], "Bravos")
    wrong = client.post("/api/v1/me/delete-account", headers=auth(user["token"]), json={"password": "otra cosa"})
    assert (wrong.status_code, wrong.json()["code"]) == (422, "WRONG_PASSWORD")
    blocked = client.post("/api/v1/me/delete-account", headers=auth(user["token"]), json={"password": PASSWORD})
    assert (blocked.status_code, blocked.json()["code"]) == (409, "LEAVE_TEAMS_FIRST")
    left = client.post(f"/api/v1/teams/{team_id}/leave", headers=auth(user["token"]))
    assert left.status_code == 204, left.text
    done = client.post("/api/v1/me/delete-account", headers=auth(user["token"]), json={"password": PASSWORD})
    assert done.status_code == 204, done.text
    assert client.get("/api/v1/me", headers=auth(user["token"])).status_code == 401  # sesiones borradas
    login = client.post("/api/v1/auth/login", json={"email": "borrar@rival.test", "password": PASSWORD})
    assert login.status_code == 401
    again = register(client, "borrar@rival.test")  # el correo queda libre para una cuenta nueva
    assert again["user"]["email"] == "borrar@rival.test"


def test_legal_contact_comes_from_server_config(client, monkeypatch):
    """Los datos del responsable no están en el código: llegan de la configuración del servidor."""
    body = client.get("/api/v1/legal").json()
    assert set(body["contact"]) == {"name", "address", "email", "phone", "attends", "hosting", "since"}
    from app.settings import Settings

    monkeypatch.setenv("RIVAL_LEGAL_EMAIL", "privacidad@rival.example")
    assert Settings().legal_contact["email"] == "privacidad@rival.example"
