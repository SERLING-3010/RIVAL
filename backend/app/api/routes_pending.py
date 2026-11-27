"""Ruta de pendientes del usuario (Sprint 11)."""

from dataclasses import asdict

from fastapi import APIRouter
from pydantic import AwareDatetime, BaseModel

from app.api.dependencies import CtxDep, UserDep
from app.services import pending_service

router = APIRouter(prefix="/api/v1")


class PendingOut(BaseModel):
    kind: str
    title: str
    detail: str
    target: str
    target_id: int | None
    due_at: AwareDatetime | None


@router.get("/me/pending")
def my_pending(ctx: CtxDep, user: UserDep) -> list[PendingOut]:
    return [PendingOut.model_validate(asdict(i)) for i in pending_service.pending(ctx, user)]
