"""Endurecimiento (Sprint 9): auditoría de inicios de sesión fallidos y purga de sesiones vencidas.

Un inicio de sesión fallido deshace la transacción de la petición, así que se registra en una
transacción aparte. Nunca se guarda el correo ni la IP: solo una clave seudónima (SHA-256).
"""

import hashlib
from datetime import timedelta

from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session, sessionmaker

from app.persistence.database import session_scope
from app.persistence.models_audit import AuditEvent
from app.persistence.models_identity import AuthSession, UserAccount
from app.services.audit_service import record_event
from app.services.context import ServiceContext

FAILURE_WINDOW = timedelta(hours=1)
FAILURE_SPIKE = 20


def login_key(email: str) -> str:
    return hashlib.sha256(f"login|{email.strip().lower()}".encode()).hexdigest()[:32]


def record_failed_login(factory: sessionmaker[Session], base: ServiceContext, email: str, code: str) -> None:
    for session in session_scope(factory):
        ctx = ServiceContext(db=session, clock=base.clock, catalog=base.catalog,
                             session_ttl=base.session_ttl, session_idle=base.session_idle)
        user_id = session.scalar(select(UserAccount.id).where(UserAccount.email == email.strip().lower()))
        record_event(ctx, action="LOGIN_FAILED", entity="auth", entity_id=login_key(email),
                     initiated_by=user_id, after={"reason": code})


def failure_spikes(ctx: ServiceContext) -> list[str]:
    """Claves seudónimas con muchos intentos fallidos en la última hora (posible ataque de contraseñas)."""
    since = ctx.clock.now() - FAILURE_WINDOW
    return list(ctx.db.scalars(select(AuditEvent.entity_id).where(
        AuditEvent.action == "LOGIN_FAILED", AuditEvent.occurred_at >= since)
        .group_by(AuditEvent.entity_id).having(func.count() >= FAILURE_SPIKE)))


def purge_sessions(ctx: ServiceContext) -> int:
    """Borra las sesiones vencidas o inactivas: ya no sirven para entrar y solo ocupan espacio."""
    now = ctx.clock.now()
    stale = or_(AuthSession.expires_at <= now, AuthSession.last_seen_at <= now - ctx.session_idle)
    count = ctx.db.scalar(select(func.count()).select_from(AuthSession).where(stale)) or 0
    if count:
        ctx.db.execute(delete(AuthSession).where(stale))
        record_event(ctx, action="SESSIONS_PURGED", entity="auth", entity_id="sessions", initiated_by=None,
                     actor_type="SYSTEM_RULE", after={"count": count})
    return count
