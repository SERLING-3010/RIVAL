"""Traducción de errores a respuestas: mensaje comprensible + correlation_id, sin trazas internas."""

import logging
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

from app.domain.errors import (
    AuthenticationError,
    ConflictError,
    DomainError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitedError,
)
from app.services.request_context import current_correlation_id, new_correlation_id

logger = logging.getLogger("rival.api")

_STATUS_BY_TYPE: list[tuple[type[DomainError], int]] = [
    (RateLimitedError, 429),
    (AuthenticationError, 401),
    (PermissionDeniedError, 403),
    (NotFoundError, 404),
    (ConflictError, 409),
]


def _body(code: str, message: str, details: list[str] | None = None) -> dict[str, object]:
    body: dict[str, object] = {"code": code, "message": message, "correlation_id": current_correlation_id()}
    if details:
        body["details"] = details
    return body


async def _domain_handler(_request: Request, error: Exception) -> JSONResponse:
    assert isinstance(error, DomainError)
    status = next((s for t, s in _STATUS_BY_TYPE if isinstance(error, t)), 422)
    headers = {}
    if isinstance(error, RateLimitedError):
        headers["Retry-After"] = str(error.retry_after_seconds)
    return JSONResponse(_body(error.code, error.message), status_code=status, headers=headers)


async def _validation_handler(_request: Request, error: Exception) -> JSONResponse:
    assert isinstance(error, RequestValidationError)
    fields = sorted({".".join(str(p) for p in e["loc"][1:]) or "cuerpo" for e in error.errors()})
    return JSONResponse(
        _body("VALIDATION_ERROR", "Revisa los campos marcados e inténtalo de nuevo.", fields), status_code=422
    )


async def _unexpected_handler(_request: Request, error: Exception) -> JSONResponse:
    logger.exception("Error no controlado correlation_id=%s", current_correlation_id(), exc_info=error)
    return JSONResponse(
        _body("INTERNAL_ERROR", "Algo salió mal de nuestro lado. Inténtalo de nuevo en un momento."),
        status_code=500,
    )


def install_error_handling(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, _domain_handler)
    app.add_exception_handler(RequestValidationError, _validation_handler)
    app.add_exception_handler(Exception, _unexpected_handler)

    @app.middleware("http")
    async def correlation_and_headers(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        correlation_id = new_correlation_id()
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response
