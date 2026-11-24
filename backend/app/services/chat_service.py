"""Chat del partido (Sprint 14): escriben y leen solo quienes juegan o pitan ese partido.

Participantes: miembros de los dos equipos, jugadores prestados activos para el partido y el árbitro
asignado (pendiente o aceptado). Para cualquier otra persona el partido no existe (404).
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import func, select

from app.domain import chat_rules
from app.domain.contract_rules import ContractStatus
from app.domain.errors import ConflictError, NotFoundError, PermissionDeniedError
from app.persistence.models_chat import MatchChatMessage
from app.persistence.models_contracts import MatchContract
from app.persistence.models_identity import UserAccount
from app.persistence.models_league_matches import RefereeAssignment
from app.services import loan_service
from app.services.audit_service import record_event
from app.services.context import ServiceContext
from app.services.contract_queries import load_contract, side_teams


@dataclass(frozen=True)
class ChatMessageView:
    id: int
    author_id: int
    author_name: str
    body: str | None  # None si el autor lo borró (salvo para moderación)
    created_at: datetime
    deleted: bool
    mine: bool


@dataclass(frozen=True)
class ChatPageView:
    contract_id: int
    writable: bool
    messages: list[ChatMessageView]


def participants(ctx: ServiceContext, contract: MatchContract) -> set[int]:
    ids: set[int] = set()
    for team in side_teams(ctx, contract).values():
        ids |= {m.user_id for m in team.memberships}
        ids |= loan_service.active_players(ctx, contract.id, team.id)
    referee = ctx.db.scalar(select(RefereeAssignment.referee_id).where(
        RefereeAssignment.contract_id == contract.id, RefereeAssignment.status.in_(("PENDING", "ACCEPTED"))))
    if referee is not None:
        ids.add(referee)
    return ids


def _participant_contract(ctx: ServiceContext, actor: UserAccount, contract_id: int,
                          lock: bool = False) -> MatchContract:
    contract = load_contract(ctx, contract_id, lock=lock)
    if actor.id not in participants(ctx, contract):
        raise NotFoundError("CONTRACT_NOT_FOUND", "El contrato no existe.")
    return contract


def _closed(ctx: ServiceContext, contract: MatchContract) -> ConflictError | None:
    return chat_rules.closed_reason(loan_service.kickoff_of(ctx, contract), ctx.clock.now(),
                                    contract.status == ContractStatus.CANCELLED)


def view_messages(ctx: ServiceContext, contract_id: int, viewer_id: int, after_id: int,
                  show_deleted: bool) -> list[ChatMessageView]:
    rows = ctx.db.execute(
        select(MatchChatMessage, UserAccount.display_name)
        .join(UserAccount, UserAccount.id == MatchChatMessage.author_id)
        .where(MatchChatMessage.contract_id == contract_id, MatchChatMessage.id > after_id)
        .order_by(MatchChatMessage.id).limit(chat_rules.PAGE_SIZE))
    return [ChatMessageView(id=m.id, author_id=m.author_id, author_name=name,
                            body=m.body if show_deleted or m.deleted_at is None else None,
                            created_at=m.created_at, deleted=m.deleted_at is not None,
                            mine=m.author_id == viewer_id) for m, name in rows]


def read(ctx: ServiceContext, actor: UserAccount, contract_id: int, after_id: int = 0) -> ChatPageView:
    contract = _participant_contract(ctx, actor, contract_id)
    return ChatPageView(contract_id=contract.id, writable=_closed(ctx, contract) is None,
                        messages=view_messages(ctx, contract.id, actor.id, after_id, show_deleted=False))


def post(ctx: ServiceContext, actor: UserAccount, contract_id: int, text: str) -> MatchChatMessage:
    contract = _participant_contract(ctx, actor, contract_id, lock=True)
    closed = _closed(ctx, contract)
    if closed is not None:
        raise closed
    body = chat_rules.clean_body(text)
    since = ctx.clock.now() - timedelta(minutes=1)
    chat_rules.check_rate(ctx.db.scalar(select(func.count()).select_from(MatchChatMessage).where(
        MatchChatMessage.contract_id == contract.id, MatchChatMessage.author_id == actor.id,
        MatchChatMessage.created_at > since)) or 0)
    message = MatchChatMessage(contract_id=contract.id, author_id=actor.id, body=body, created_at=ctx.clock.now())
    ctx.db.add(message)
    ctx.db.flush()
    return message


def delete(ctx: ServiceContext, actor: UserAccount, message_id: int) -> MatchChatMessage:
    message = ctx.db.get(MatchChatMessage, message_id, with_for_update=True)
    if message is None or actor.id not in participants(ctx, load_contract(ctx, message.contract_id)):
        raise NotFoundError("MESSAGE_NOT_FOUND", "El mensaje no existe.")
    if message.author_id != actor.id:
        raise PermissionDeniedError("AUTHOR_ONLY", "Solo quien escribió el mensaje puede borrarlo.")
    if message.deleted_at is None:
        message.deleted_at = ctx.clock.now()
        ctx.db.flush()
        record_event(ctx, action="CHAT_MESSAGE_DELETED", entity="match_contract", entity_id=message.contract_id,
                     initiated_by=actor.id, after={"message_id": message.id})
    return message
