"""Rutas de identidad y catálogo."""

from dataclasses import asdict

from fastapi import APIRouter, Request, Response

from app.api.dependencies import ClientKeyDep, CtxDep, IpLimitsDep, LimiterDep, TokenDep, UserDep
from app.api.schemas_auth import AddRoleRequest, LoginRequest, RegisterRequest, SessionOut, UserOut
from app.domain.errors import AuthenticationError, RateLimitedError
from app.services import auth_service, security_service
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
def login(
    request: Request, body: LoginRequest, ctx: CtxDep, limiter: LimiterDep, key: ClientKeyDep, ip: IpLimitsDep
) -> SessionOut:
    try:
        ip.login.hit(key, ctx.clock.now())
        token, user = auth_service.login(ctx, limiter, body.email, body.password, key)
    except (AuthenticationError, RateLimitedError) as error:
        # La transacción de esta petición se deshace; el intento fallido se audita en una aparte.
        security_service.record_failed_login(request.app.state.session_factory, ctx, body.email, error.code)
        raise
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
