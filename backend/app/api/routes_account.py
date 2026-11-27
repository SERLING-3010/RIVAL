"""Mis datos (Sprint 27): aceptar términos, descargar mis datos y eliminar la cuenta (Ley 1581)."""

from fastapi import APIRouter, Request, Response
from pydantic import Field

from app.api.dependencies import CtxDep, UserDep
from app.api.schemas_auth import StrictModel, UserOut
from app.domain.legal_rules import TERMS_VERSION
from app.services import account_export, account_service

router = APIRouter(prefix="/api/v1")


class AcceptTermsBody(StrictModel):
    version: str = Field(max_length=20)


class DeleteAccountBody(StrictModel):
    password: str = Field(max_length=128)


@router.get("/legal/terms-version")
def terms_version() -> dict[str, str]:
    return {"version": TERMS_VERSION}


@router.get("/legal")
def legal(request: Request) -> dict[str, object]:
    """Versión de los textos y datos del responsable (Ley 1581), tomados de la configuración del servidor.
    Lo que falte llega vacío y la app muestra «por definir». No pide sesión: se lee antes de registrarse."""
    return {"version": TERMS_VERSION, "contact": request.app.state.settings.legal_contact}


@router.post("/me/accept-terms")
def accept_terms(body: AcceptTermsBody, ctx: CtxDep, user: UserDep) -> UserOut:
    return UserOut.from_account(account_service.accept_terms(ctx, user, body.version))


@router.get("/me/data-export")
def data_export(ctx: CtxDep, user: UserDep) -> dict[str, object]:
    return account_export.export(ctx, user)


@router.post("/me/delete-account", status_code=204)
def delete_account(body: DeleteAccountBody, ctx: CtxDep, user: UserDep) -> Response:
    account_service.delete_account(ctx, user, body.password)
    return Response(status_code=204)
