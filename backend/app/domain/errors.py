"""Errores de dominio con código estable y mensaje en español para el usuario."""


class DomainError(Exception):
    """Regla de negocio violada. El código es estable; el mensaje es para personas."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class NotFoundError(DomainError):
    """El recurso no existe o el actor no puede verlo."""


class PermissionDeniedError(DomainError):
    """El actor no tiene permiso para esta acción."""


class ConflictError(DomainError):
    """La acción choca con el estado actual (duplicado, ya resuelto, etc.)."""


class AuthenticationError(DomainError):
    """Credenciales o sesión inválidas."""


class RateLimitedError(DomainError):
    """Demasiados intentos; hay que esperar."""

    def __init__(self, code: str, message: str, retry_after_seconds: int) -> None:
        super().__init__(code, message)
        self.retry_after_seconds = retry_after_seconds
