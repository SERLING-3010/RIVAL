"""Términos, privacidad y derechos sobre los datos (Sprint 27). Ley 1581 de 2012 (Colombia).

- Para usar RIVAL hay que aceptar la versión vigente de los Términos y de la Política de tratamiento
  de datos, y declarar ser mayor de 18. Se guarda qué versión se aceptó y cuándo.
- Supresión (decisión del dueño, 25/11/2026): la cuenta se anonimiza. Se borran los datos que
  identifican a la persona y su historial (partidos, resultados, auditoría) se conserva sin ellos.
Los textos son BORRADORES [POR VERIFICAR con abogado] y están en `docs/legal/`.
"""

from datetime import date

from app.domain.errors import DomainError

TERMS_VERSION = "2026-11-25"  # cambia cuando cambian los textos; obliga a aceptar de nuevo
DELETED_NAME = "Jugador eliminado"
DELETED_BIRTH_DATE = date(1900, 1, 1)  # la columna no admite vacío; no identifica a nadie
DELETED_PLACE = "—"


def require_acceptance(accepted: bool) -> None:
    if not accepted:
        raise DomainError("TERMS_NOT_ACCEPTED",
                          "Para usar RIVAL debes aceptar los Términos y la Política de privacidad.")


def needs_terms(accepted_version: str | None) -> bool:
    return accepted_version != TERMS_VERSION


def check_version(version: str) -> None:
    """Solo se acepta la versión vigente (la app pudo quedarse con un texto viejo)."""
    if version != TERMS_VERSION:
        raise DomainError("TERMS_VERSION_OUTDATED", "Hay una versión nueva de los términos. Actualiza la app.")


def deleted_email(user_id: int) -> str:
    """Correo imposible de usar (dominio .invalid) y único, para liberar el original."""
    return f"eliminado-{user_id}@rival.invalid"
