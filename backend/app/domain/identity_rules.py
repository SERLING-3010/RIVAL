"""Validaciones de identidad: correo, nombre visible, contraseña y lugares (ciudad, barrio).

Se valida y se rechaza; nunca se altera en silencio lo que escribió la persona
(solo se quitan espacios al inicio y al final y el correo pasa a minúsculas).
"""

import re

from app.domain.errors import DomainError

MIN_PASSWORD_LENGTH = 10
MAX_PASSWORD_LENGTH = 128
COMMON_PASSWORDS: frozenset[str] = frozenset(
    {
        "1234567890",
        "12345678910",
        "contraseña123",
        "contrasena123",
        "password123",
        "qwertyuiop",
        "futbol12345",
        "colombia123",
    }
)
_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_NAME_PATTERN = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' .-]{2,60}$")
_PLACE_PATTERN = re.compile(r"^[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ' .,#-]{2,60}$")


def normalize_email(email: str) -> str:
    cleaned = email.strip().lower()
    if len(cleaned) > 254 or not _EMAIL_PATTERN.match(cleaned):
        raise DomainError("INVALID_EMAIL", "Escribe un correo válido, por ejemplo nombre@correo.com.")
    return cleaned


def validate_display_name(name: str) -> str:
    cleaned = name.strip()
    if not _NAME_PATTERN.match(cleaned):
        raise DomainError(
            "INVALID_NAME",
            "El nombre debe tener entre 2 y 60 letras; se permiten tildes, ñ, espacios y guiones.",
        )
    return cleaned


def validate_password(password: str) -> None:
    if not MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH:
        raise DomainError(
            "WEAK_PASSWORD",
            f"La contraseña debe tener entre {MIN_PASSWORD_LENGTH} y {MAX_PASSWORD_LENGTH} caracteres.",
        )
    if password.lower() in COMMON_PASSWORDS:
        raise DomainError("WEAK_PASSWORD", "Esa contraseña es muy común. Prueba con una frase.")


def validate_place_name(value: str, field: str) -> str:
    cleaned = value.strip()
    if not _PLACE_PATTERN.match(cleaned):
        raise DomainError("INVALID_PLACE", f"Escribe un nombre de {field} válido (2 a 60 caracteres).")
    return cleaned
