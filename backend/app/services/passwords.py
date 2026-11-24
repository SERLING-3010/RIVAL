"""Hash de contraseñas con Argon2id según la guía de OWASP (19 MiB, 2 iteraciones, 1 hilo)."""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

_HASHER = PasswordHasher(time_cost=2, memory_cost=19 * 1024, parallelism=1)

# Hash de una contraseña que nadie conoce: se verifica contra él cuando el correo no existe,
# para que la respuesta tarde lo mismo y no revele si la cuenta existe.
_DUMMY_HASH = _HASHER.hash("rival-dummy-password-never-used")


def hash_password(password: str) -> str:
    return _HASHER.hash(password)


def verify_password(password_hash: str | None, password: str) -> bool:
    try:
        return _HASHER.verify(password_hash or _DUMMY_HASH, password) and password_hash is not None
    except (VerificationError, InvalidHashError):
        return False
