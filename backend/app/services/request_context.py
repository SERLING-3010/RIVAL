"""Identificador de correlación por petición, para unir logs, errores y auditoría."""

import uuid
from contextvars import ContextVar

_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="no-request")


def new_correlation_id() -> str:
    value = uuid.uuid4().hex
    _correlation_id.set(value)
    return value


def current_correlation_id() -> str:
    return _correlation_id.get()
