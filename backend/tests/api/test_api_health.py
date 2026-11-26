"""Salud del servicio y arranque sin crear tablas (Sprint 28)."""

from app.main import create_app
from app.settings import Settings


def test_health_reports_ok(client):
    response = client.get("/api/v1/health")
    assert (response.status_code, response.json()) == (200, {"status": "ok"})


def test_auto_schema_can_be_turned_off(monkeypatch):
    monkeypatch.setenv("RIVAL_AUTO_SCHEMA", "false")
    assert Settings().auto_schema is False
    monkeypatch.setenv("RIVAL_AUTO_SCHEMA", "true")
    assert Settings().auto_schema is True
    assert create_app(Settings()) is not None
