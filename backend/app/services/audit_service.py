"""Registro de eventos de auditoría con hash SHA-256 encadenado.

Cada evento guarda el hash del anterior; alterar uno rompe la cadena y `verify_chain`
lo detecta. Es resistente a manipulación, no inmutable: un administrador con acceso
directo a la base podría reescribir toda la cadena (riesgo documentado).
"""

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models_audit import AuditEvent, AuditHead
from app.services.context import ServiceContext
from app.services.request_context import current_correlation_id

SOFTWARE_VERSION = "0.1.0"
GENESIS_HASH = "0" * 64


def _to_json(data: Mapping[str, Any] | None) -> str | None:
    if data is None:
        return None
    return json.dumps(data, ensure_ascii=False, sort_keys=True, default=str)


def _compute_hash(event: AuditEvent) -> str:
    payload = "|".join(
        [
            str(event.chain_position),
            event.software_version,
            event.prev_hash,
            event.occurred_at.isoformat(),
            event.actor_type,
            str(event.initiated_by),
            str(event.approved_by),
            event.action,
            event.entity,
            event.entity_id,
            event.before_json or "",
            event.after_json or "",
            event.correlation_id,
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def record_event(
    ctx: ServiceContext,
    *,
    action: str,
    entity: str,
    entity_id: int | str,
    initiated_by: int | None,
    approved_by: int | None = None,
    actor_type: str = "HUMAN",
    before: Mapping[str, Any] | None = None,
    after: Mapping[str, Any] | None = None,
) -> AuditEvent:
    # Bloquea el eslabón final: dos peticiones simultáneas escriben una después de la otra.
    head = ctx.db.get(AuditHead, 1, with_for_update=True)
    if head is None:
        raise RuntimeError("Falta la fila audit_head; ejecuta create_schema")
    event = AuditEvent(
        chain_position=head.last_position + 1,
        occurred_at=ctx.clock.now(),
        actor_type=actor_type,
        initiated_by=initiated_by,
        approved_by=approved_by,
        action=action,
        entity=entity,
        entity_id=str(entity_id),
        before_json=_to_json(before),
        after_json=_to_json(after),
        correlation_id=current_correlation_id(),
        software_version=SOFTWARE_VERSION,
        prev_hash=head.last_hash,
    )
    event.integrity_hash = _compute_hash(event)
    ctx.db.add(event)
    head.last_hash = event.integrity_hash
    head.last_position = event.chain_position
    ctx.db.flush()
    return event


def verify_chain(db: Session) -> bool:
    """Recorre la cadena en orden y comprueba cada hash y que el final coincida con audit_head."""
    expected_prev = GENESIS_HASH
    expected_position = 0
    for event in db.scalars(select(AuditEvent).order_by(AuditEvent.chain_position)):
        expected_position += 1
        if (
            event.chain_position != expected_position
            or event.prev_hash != expected_prev
            or _compute_hash(event) != event.integrity_hash
        ):
            return False
        expected_prev = event.integrity_hash
    head = db.get(AuditHead, 1)
    return head is not None and head.last_hash == expected_prev and head.last_position == expected_position
