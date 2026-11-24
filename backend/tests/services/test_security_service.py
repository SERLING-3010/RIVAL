from datetime import timedelta

from app.persistence.models_audit import AuditEvent
from app.persistence.models_identity import AuthSession
from app.services import auth_service, health_service, security_service
from app.services.rate_limiter import LoginRateLimiter
from tests.conftest import register_input


def test_purge_removes_only_stale_sessions(ctx, clock):
    auth_service.register_user(ctx, register_input())
    limiter = LoginRateLimiter()
    auth_service.login(ctx, limiter, "jugador@rival.test", "mi equipo juega los sábados", "ip")
    clock.advance(timedelta(hours=80))  # más que la inactividad permitida (72 h)
    auth_service.login(ctx, limiter, "jugador@rival.test", "mi equipo juega los sábados", "ip")
    assert security_service.purge_sessions(ctx) == 1
    assert ctx.db.query(AuthSession).count() == 1
    assert ctx.db.query(AuditEvent).filter(AuditEvent.action == "SESSIONS_PURGED").count() == 1
    assert security_service.purge_sessions(ctx) == 0


def test_failure_spike_is_a_health_finding(ctx):
    from app.services.audit_service import record_event

    for _ in range(security_service.FAILURE_SPIKE):
        record_event(ctx, action="LOGIN_FAILED", entity="auth", entity_id=security_service.login_key("x@r.test"),
                     initiated_by=None, after={"reason": "INVALID_CREDENTIALS"})
    assert [f.code for f in health_service.run_checks(ctx)] == ["LOGIN_FAILURE_SPIKE"]
    assert "x@r.test" not in security_service.login_key("x@r.test")
