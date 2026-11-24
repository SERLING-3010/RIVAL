from sqlalchemy import select

from app.persistence.models_audit import AuditEvent
from app.services import audit_service, auth_service
from tests.conftest import register_input


def test_registration_is_audited_with_actor(ctx):
    user = auth_service.register_user(ctx, register_input())
    events = ctx.db.scalars(select(AuditEvent)).all()
    assert [e.action for e in events] == ["USER_REGISTERED"]
    assert events[0].initiated_by == user.id
    assert events[0].actor_type == "HUMAN"
    assert "password" not in (events[0].after_json or "")


def test_chain_verifies_and_detects_tampering(ctx):
    auth_service.register_user(ctx, register_input(email="a@rival.test"))
    auth_service.register_user(ctx, register_input(email="b@rival.test"))
    assert audit_service.verify_chain(ctx.db) is True
    first = ctx.db.scalars(select(AuditEvent).order_by(AuditEvent.id)).first()
    first.after_json = '{"display_name": "Alterado"}'
    ctx.db.flush()
    assert audit_service.verify_chain(ctx.db) is False


def test_fork_with_same_prev_hash_is_rejected(ctx):
    import pytest
    from sqlalchemy.exc import IntegrityError

    auth_service.register_user(ctx, register_input())
    first = ctx.db.scalars(select(AuditEvent)).first()
    clone = AuditEvent(
        chain_position=99, occurred_at=first.occurred_at, actor_type="HUMAN", initiated_by=None,
        approved_by=None, action="FORK", entity="x", entity_id="1", before_json=None, after_json=None,
        correlation_id="c", software_version="0.1.0", prev_hash=first.prev_hash, integrity_hash="f" * 64,
    )
    ctx.db.add(clone)
    with pytest.raises(IntegrityError):
        ctx.db.flush()


def test_deleting_last_event_is_detected(ctx):
    auth_service.register_user(ctx, register_input(email="a@rival.test"))
    auth_service.register_user(ctx, register_input(email="b@rival.test"))
    last = ctx.db.scalars(select(AuditEvent).order_by(AuditEvent.chain_position.desc())).first()
    ctx.db.delete(last)
    ctx.db.flush()
    assert audit_service.verify_chain(ctx.db) is False
