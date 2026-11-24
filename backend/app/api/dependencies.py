"""Dependencias de FastAPI: contexto de servicio por petición y usuario autenticado."""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Header, Request

from app.domain.errors import AuthenticationError
from app.persistence.database import session_scope
from app.persistence.models_identity import UserAccount
from app.services import auth_service
from app.services.context import ServiceContext
from app.services.ip_limiter import login_ip_limiter, register_limiter
from app.services.rate_limiter import LoginRateLimiter


def get_ctx(request: Request) -> Iterator[ServiceContext]:
    state = request.app.state
    for session in session_scope(state.session_factory):
        yield ServiceContext(
            db=session,
            clock=state.clock,
            catalog=state.catalog,
            session_ttl=state.settings.session_ttl,
            session_idle=state.settings.session_idle,
        )


def get_limiter(request: Request) -> LoginRateLimiter:
    limiter: LoginRateLimiter = request.app.state.login_limiter
    return limiter


def ip_limits(request: Request) -> "IpLimits":
    limits: IpLimits = request.app.state.ip_limits
    return limits


class IpLimits:
    """Límites por IP para registro e inicio de sesión."""

    def __init__(self) -> None:
        self.register = register_limiter()
        self.login = login_ip_limiter()


def client_key(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def bearer_token(authorization: Annotated[str | None, Header()] = None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationError("SESSION_EXPIRED", "Inicia sesión para continuar.")
    return authorization.removeprefix("Bearer ").strip()


CtxDep = Annotated[ServiceContext, Depends(get_ctx)]
TokenDep = Annotated[str, Depends(bearer_token)]


def current_user(ctx: CtxDep, token: TokenDep) -> UserAccount:
    return auth_service.authenticate(ctx, token)


UserDep = Annotated[UserAccount, Depends(current_user)]
LimiterDep = Annotated[LoginRateLimiter, Depends(get_limiter)]
ClientKeyDep = Annotated[str, Depends(client_key)]
IpLimitsDep = Annotated[IpLimits, Depends(ip_limits)]
