"""Alineación táctica antes del partido (Sprint 19, P2 del Sprint 0: "alineaciones tácticas avanzadas").

Titulares exactos según la modalidad, cada uno con su posición, y suplentes. En fútbol y microfútbol
hay formación: sus líneas suman los jugadores de campo (sin el arquero). Solo entran convocados que
dijeron que van. No es la planilla del Sprint 7, que registra quién jugó y los goles después.
"""

import re

from app.domain.errors import DomainError

FORMATION_SPORTS = {"FOOTBALL", "FUTSAL"}
MAX_SUBS = 12
MAX_POSITION = 20
_FORMATION = re.compile(r"^[1-9](-[1-9]){0,4}$")

SUGGESTED = {
    "F5": ["2-2", "1-2-1"],
    "MICRO5": ["2-2", "1-2-1"],
    "F7": ["2-3-1", "3-2-1", "3-3"],
    "F8": ["3-3-1", "3-2-2", "2-3-2"],
    "F11": ["4-4-2", "4-3-3", "3-5-2"],
}


def suggested_formations(modality_code: str) -> list[str]:
    return SUGGESTED.get(modality_code, [])


def validate_formation(sport_code: str, players_per_side: int, formation: str | None) -> str | None:
    if sport_code not in FORMATION_SPORTS:
        if formation:
            raise DomainError("FORMATION_NOT_USED", "Este deporte no usa formación; deja solo las posiciones.")
        return None
    if formation is None:
        return None
    clean = formation.strip()
    if not _FORMATION.match(clean) or sum(int(n) for n in clean.split("-")) != players_per_side - 1:
        raise DomainError("INVALID_FORMATION",
                          f"La formación debe sumar {players_per_side - 1} jugadores de campo (sin el arquero), "
                          "por ejemplo 2-3-1.")
    return clean


def validate_slots(starters: list[tuple[int, str]], subs: list[int], players_per_side: int,
                   eligible: set[int]) -> list[tuple[int, str]]:
    """Titulares con su posición limpia; lanza si algo no cuadra."""
    if len(starters) != players_per_side:
        raise DomainError("STARTERS_COUNT", f"Elige exactamente {players_per_side} titulares.")
    if len(subs) > MAX_SUBS:
        raise DomainError("TOO_MANY_SUBS", f"Máximo {MAX_SUBS} suplentes.")
    everyone = [u for u, _ in starters] + subs
    if len(set(everyone)) != len(everyone):
        raise DomainError("DUPLICATED_PLAYER", "Un jugador no puede estar dos veces en la alineación.")
    if not set(everyone) <= eligible:
        raise DomainError("NOT_CALLED_UP", "Solo entran convocados que confirmaron que van.")
    clean = [(u, " ".join(p.split())) for u, p in starters]
    if any(not 1 <= len(p) <= MAX_POSITION for _, p in clean):
        raise DomainError("INVALID_POSITION", f"Cada titular necesita una posición de 1 a {MAX_POSITION} caracteres.")
    return clean
