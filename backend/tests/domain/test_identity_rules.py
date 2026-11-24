import pytest

from app.domain.errors import DomainError
from app.domain.identity_rules import (
    MIN_PASSWORD_LENGTH,
    normalize_email,
    validate_display_name,
    validate_password,
    validate_place_name,
)


def test_email_is_trimmed_and_lowercased():
    assert normalize_email("  Sergio.Rodriguez@Example.COM ") == "sergio.rodriguez@example.com"


def test_invalid_email_rejected():
    with pytest.raises(DomainError) as error:
        normalize_email("sin-arroba")
    assert error.value.code == "INVALID_EMAIL"


def test_display_name_accepts_tildes_and_enie():
    assert validate_display_name("  José Peña Ñañez ") == "José Peña Ñañez"


def test_display_name_too_short_rejected():
    with pytest.raises(DomainError):
        validate_display_name("J")


def test_password_minimum_length():
    with pytest.raises(DomainError) as error:
        validate_password("a" * (MIN_PASSWORD_LENGTH - 1))
    assert error.value.code == "WEAK_PASSWORD"


def test_common_password_rejected():
    with pytest.raises(DomainError):
        validate_password("contraseña123")


def test_long_passphrase_with_spaces_accepted():
    validate_password("mi equipo juega los sábados")


def test_place_name_rejects_empty():
    with pytest.raises(DomainError) as error:
        validate_place_name("   ", field="barrio")
    assert error.value.code == "INVALID_PLACE"


def test_place_name_keeps_accents():
    assert validate_place_name(" El Prado ", field="barrio") == "El Prado"
