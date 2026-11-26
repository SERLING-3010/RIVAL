"""Notificaciones push (Sprint 24). Decisión del dueño (25/11/2026): avisos breves y sin datos.

El texto pasa por Expo y por Apple o Google y se ve en la pantalla bloqueada, así que nunca lleva
nombres, equipos, marcadores, horarios ni lugares: solo qué tipo de cosa espera en la app.
"""

import re

from app.domain.errors import DomainError

# Tipo de pendiente → aviso. Solo frases genéricas, sin datos.
MESSAGES: dict[str, str] = {
    "SIGN_CONTRACT": "Hay un contrato por firmar.",
    "REPORT_RESULT": "Hay un marcador por reportar.",
    "RESULT_DISPUTED": "Hay un marcador en disputa.",
    "CALLUP": "Tienes una convocatoria nueva.",
    "CONFIRM_GOAL_KINDS": "Hay goles especiales por confirmar.",
    "TRANSFER_PLAYER": "Tienes una oferta de traspaso.",
    "TRANSFER_OWNER": "Hay una oferta por un jugador de tu equipo.",
    "JOIN_REQUESTS": "Alguien quiere unirse a tu equipo.",
    "LEAGUE_REQUESTS": "Hay solicitudes nuevas en tu liga.",
    "REFEREE_ASSIGNMENT": "Tienes un partido para arbitrar.",
    "REFEREE_RESULT": "Hay un resultado por registrar como árbitro.",
    "CONFIRM_BOOKING": "Hay una reserva por confirmar.",
    "RATE_TEAMMATES": "Ya puedes valorar a tus compañeros.",
    "LOAN_PLAYER": "Tienes una propuesta de préstamo.",
    "LOAN_OWNER": "Hay una propuesta de préstamo en tu equipo.",
}
GENERIC = "Tienes algo pendiente en RIVAL."
TITLE = "RIVAL"
MAX_DEVICES_PER_USER = 5

_TOKEN = re.compile(r"^Expo(nent)?PushToken\[[A-Za-z0-9_-]{10,120}\]$")


def validate_token(token: str) -> str:
    token = token.strip()
    if not _TOKEN.fullmatch(token):
        raise DomainError("INVALID_PUSH_TOKEN", "El identificador de notificaciones del teléfono no es válido.")
    return token


def item_key(kind: str, target_id: int | None) -> str:
    """Identifica un pendiente para avisar una sola vez por él."""
    return f"{kind}:{target_id if target_id is not None else '-'}"


def body_for(kinds: list[str]) -> str:
    """Un solo aviso por persona y por ronda: el del pendiente, o un resumen si son varios."""
    if len(kinds) == 1:
        return MESSAGES.get(kinds[0], GENERIC)
    return f"Tienes {len(kinds)} cosas nuevas por revisar en RIVAL."
