"""Rutas de identidad y catálogo."""

from dataclasses import asdict

from fastapi import APIRouter, Request, Response

from app.api.dependencies import ClientKeyDep, CtxDep, IpLimitsDep, LimiterDep, TokenDep, UserDep
from app.api.schemas_auth import AddRoleRequest, LoginRequest, RegisterRequest, SessionOut, UserOut
from app.services import auth_service
from app.services.inputs import RegisterInput

router = APIRouter(prefix="/api/v1")


@router.get("/catalog/sports")
def sports_catalog(request: Request) -> dict[str, object]:
    return {"sports": [asdict(s) for s in request.app.state.catalog.sports]}


@router.post("/auth/register", status_code=201)
def register(
    body: RegisterRequest, ctx: CtxDep, limiter: LimiterDep, key: ClientKeyDep, ip: IpLimitsDep
) -> SessionOut:
    ip.register.hit(key, ctx.clock.now())
    auth_service.register_user(ctx, RegisterInput(**body.model_dump()))
    token, user = auth_service.login(ctx, limiter, body.email, body.password, key)
    return SessionOut(token=token, user=UserOut.from_account(user))


@router.post("/auth/login")
def login(body: LoginRequest, ctx: CtxDep, limiter: LimiterDep, key: ClientKeyDep, ip: IpLimitsDep) -> SessionOut:
    ip.login.hit(key, ctx.clock.now())
    token, user = auth_service.login(ctx, limiter, body.email, body.password, key)
    return SessionOut(token=token, user=UserOut.from_account(user))


@router.post("/auth/logout", status_code=204)
def logout(ctx: CtxDep, token: TokenDep) -> Response:
    auth_service.logout(ctx, token)
    return Response(status_code=204)


@router.get("/me")
def me(user: UserDep) -> UserOut:
    return UserOut.from_account(user)


@router.post("/me/roles")
def add_role(body: AddRoleRequest, ctx: CtxDep, user: UserDep) -> UserOut:
    return UserOut.from_account(auth_service.add_role(ctx, user, body.role, body.sports))
