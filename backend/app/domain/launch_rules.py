"""Alcance del lanzamiento (Sprint 29). Decisión del dueño (26/11/2026): lanzar solo con fútbol, sin
árbitros y sin establecimientos deportivos; eso llega más adelante.

No se borra nada: se apaga por configuración (`RIVAL_SPORTS`, `RIVAL_ENABLE_REFEREES`,
`RIVAL_ENABLE_VENUES`). Por defecto todo está prendido (desarrollo y pruebas); el despliegue del
piloto los apaga en `deploy/.env`.
"""

from dataclasses import dataclass

from app.domain.errors import DomainError, NotFoundError
from app.domain.match_rules import PlaceKind, RefereeMode
from app.domain.roles import UserRole


@dataclass(frozen=True)
class Features:
    sports: frozenset[str] | None = None  # None = todos los del catálogo
    referees: bool = True
    venues: bool = True


ALL = Features()


def check_role(features: Features, role: UserRole) -> None:
    """Sin árbitros ni establecimientos, solo se puede ser jugador o DT."""
    if (role == UserRole.REFEREE and not features.referees) or (
            role == UserRole.VENUE_OWNER and not features.venues):
        raise DomainError("ROLE_NOT_AVAILABLE", "Por ahora RIVAL es solo para jugadores y DT.")


def match_terms(features: Features, referee: RefereeMode, place: PlaceKind) -> RefereeMode:
    """Valida árbitro y lugar de un partido. Sin árbitros, «da igual» pasa a «sin árbitro»."""
    if not features.referees:
        if referee == RefereeMode.WITH:
            raise DomainError("REFEREES_NOT_AVAILABLE", "Por ahora los partidos son sin árbitro.")
        referee = RefereeMode.WITHOUT
    if not features.venues and place == PlaceKind.VENUE:
        raise DomainError("VENUES_NOT_AVAILABLE",
                          "Por ahora no hay reservas en establecimientos: elige un lugar informal o por acordar.")
    return referee


def default_referee(features: Features) -> RefereeMode:
    """Árbitro de los partidos que crea RIVAL (calendario de liga y copa)."""
    return RefereeMode.WITH if features.referees else RefereeMode.WITHOUT


def require(enabled: bool, what: str) -> None:
    """Para rutas de una parte apagada: responde como si no existiera."""
    if not enabled:
        raise NotFoundError("FEATURE_DISABLED", f"Por ahora RIVAL no tiene {what}.")
