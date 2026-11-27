"""Lectura del chat para moderación (Sprint 14).

Una persona moderadora solo lee el chat de un partido con un reporte abierto sobre él, y nunca si
participa del partido o está involucrada en esos reportes. Ve también lo que el autor borró.
"""

from sqlalchemy import select

from app.domain.errors import NotFoundError, PermissionDeniedError
from app.persistence.models_identity import UserAccount
from app.persistence.models_moderation import Report
from app.services import sanction_service
from app.services.audit_service import record_event
from app.services.chat_service import ChatPageView, view_messages
from app.services.context import ServiceContext
from app.services.contract_queries import load_contract
from app.services.match_participants import participants


def read_for_report(ctx: ServiceContext, actor: UserAccount, contract_id: int, after_id: int = 0) -> ChatPageView:
    sanction_service.require_moderator(ctx, actor)
    reports = list(ctx.db.scalars(select(Report).where(Report.contract_id == contract_id, Report.status == "OPEN")))
    if not reports:
        raise NotFoundError("NO_OPEN_REPORT", "Ese partido no tiene reportes abiertos.")
    contract = load_contract(ctx, contract_id)
    if actor.id in participants(ctx, contract) or any(sanction_service.involved(ctx, r, actor.id) for r in reports):
        raise PermissionDeniedError("CONFLICT_OF_INTEREST", "No puedes revisar un partido en el que estás involucrado.")
    if after_id == 0:
        record_event(ctx, action="CHAT_READ_BY_MODERATOR", entity="match_contract", entity_id=contract.id,
                     initiated_by=actor.id, after={"reports": [r.id for r in reports]})
    return ChatPageView(contract_id=contract.id, writable=False,
                        messages=view_messages(ctx, contract.id, actor.id, after_id, show_deleted=True))
