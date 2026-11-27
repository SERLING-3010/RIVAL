"""Inicios de sesión fallidos auditados aparte, sin correo (Sprint 9)."""

from app.persistence.models_audit import AuditEvent
from tests.api.conftest import register


def test_failed_login_is_audited_without_email(client):
    register(client, "ana@r.test")
    bad = client.post("/api/v1/auth/login", json={"email": "ana@r.test", "password": "una clave equivocada"})
    assert bad.status_code == 401
    unknown = client.post("/api/v1/auth/login", json={"email": "nadie@r.test", "password": "una clave equivocada"})
    assert unknown.status_code == 401
    with client.app.state.session_factory() as session:
        failed = session.query(AuditEvent).filter(AuditEvent.action == "LOGIN_FAILED").all()
        assert len(failed) == 2
        assert failed[0].initiated_by is not None and failed[1].initiated_by is None
        assert all("@" not in (e.entity_id + (e.after_json or "")) for e in failed)
