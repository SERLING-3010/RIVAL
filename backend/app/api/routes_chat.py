"""Rutas del chat del partido (Sprint 14)."""

from dataclasses import asdict

from fastapi import APIRouter, Query
from pydantic import AwareDatetime, BaseModel, Field

from app.api.dependencies import CtxDep, UserDep
from app.api.schemas_auth import StrictModel
from app.services import chat_moderation, chat_service
from app.services.chat_service import ChatPageView

router = APIRouter(prefix="/api/v1")


class ChatBody(StrictModel):
    text: str = Field(max_length=2000)


class ChatMessageOut(BaseModel):
    id: int
    author_id: int
    author_name: str
    body: str | None
    created_at: AwareDatetime
    deleted: bool
    mine: bool


class ChatPageOut(BaseModel):
    contract_id: int
    writable: bool
    messages: list[ChatMessageOut]


def _out(page: ChatPageView) -> ChatPageOut:
    return ChatPageOut.model_validate(asdict(page))


@router.get("/contracts/{contract_id}/chat")
def read_chat(contract_id: int, ctx: CtxDep, user: UserDep, after_id: int = Query(0, ge=0)) -> ChatPageOut:
    return _out(chat_service.read(ctx, user, contract_id, after_id))


@router.post("/contracts/{contract_id}/chat", status_code=201)
def post_message(contract_id: int, body: ChatBody, ctx: CtxDep, user: UserDep) -> ChatMessageOut:
    message = chat_service.post(ctx, user, contract_id, body.text)
    page = chat_service.read(ctx, user, contract_id, message.id - 1)
    return ChatMessageOut.model_validate(asdict(page.messages[0]))


@router.post("/chat/{message_id}/delete")
def delete_message(message_id: int, ctx: CtxDep, user: UserDep) -> dict[str, int]:
    return {"id": chat_service.delete(ctx, user, message_id).id}


@router.get("/moderation/contracts/{contract_id}/chat")
def moderator_chat(contract_id: int, ctx: CtxDep, user: UserDep, after_id: int = Query(0, ge=0)) -> ChatPageOut:
    return _out(chat_moderation.read_for_report(ctx, user, contract_id, after_id))
