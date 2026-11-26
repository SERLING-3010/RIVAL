"""Rutas de notificaciones push (Sprint 24): el teléfono se registra al iniciar sesión y se quita al salir."""

from fastapi import APIRouter, Response
from pydantic import Field

from app.api.dependencies import CtxDep, UserDep
from app.api.schemas_auth import StrictModel
from app.services import push_service

router = APIRouter(prefix="/api/v1")


class PushDeviceBody(StrictModel):
    token: str = Field(min_length=10, max_length=200)


@router.post("/me/push-devices", status_code=204)
def register_device(body: PushDeviceBody, ctx: CtxDep, user: UserDep) -> Response:
    push_service.register(ctx, user, body.token)
    return Response(status_code=204)


@router.post("/me/push-devices/remove", status_code=204)
def remove_device(body: PushDeviceBody, ctx: CtxDep, user: UserDep) -> Response:
    push_service.unregister(ctx, user, body.token)
    return Response(status_code=204)
