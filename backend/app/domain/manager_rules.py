"""Reglas del modo manager (Sprint 7, RIV-015 y RIV-016).

Las monedas RIVAL son enteros virtuales: no se compran ni se venden con dinero real
(decisión del dueño). El jugador es una persona real: ningún traspaso sin su aceptación.
"""

from enum import StrEnum

from app.domain.errors import ConflictError, DomainError
from app.domain.roles import TeamRole

STARTING_BUDGET = 1000  # [SUPUESTO] ajustable
REWARD_PLAYED = 50
REWARD_WIN_BONUS = 100
REWARD_DRAW_BONUS = 25
MAX_OFFER = 1_000_000
MAX_LINEUP = 40


class TransferStatus(StrEnum):
    PENDING_OWNER = "PENDING_OWNER"  # espera al administrador del equipo dueño
    PENDING_PLAYER = "PENDING_PLAYER"  # el dueño aceptó; espera al jugador
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"
    CANCELLED = "CANCELLED"


ACTIVE_TRANSFERS = (TransferStatus.PENDING_OWNER.value, TransferStatus.PENDING_PLAYER.value)


def result_rewards(host_score: int, guest_score: int) -> tuple[int, int]:
    """Monedas para (local, visitante) por un partido con resultado confirmado."""
    host = guest = REWARD_PLAYED
    if host_score > guest_score:
        host += REWARD_WIN_BONUS
    elif guest_score > host_score:
        guest += REWARD_WIN_BONUS
    else:
        host += REWARD_DRAW_BONUS
        guest += REWARD_DRAW_BONUS
    return host, guest


def validate_offer_amount(amount: int) -> None:
    if not 1 <= amount <= MAX_OFFER:
        raise DomainError("INVALID_OFFER_AMOUNT", "La oferta va de 1 a 1.000.000 monedas RIVAL.")


def check_balance(balance: int, amount: int) -> None:
    if balance < amount:
        raise ConflictError("INSUFFICIENT_COINS", f"Tu equipo tiene {balance} monedas; la oferta es de {amount}.")


def check_transferable(role: TeamRole) -> None:
    if role != TeamRole.PLAYER:
        raise DomainError("NOT_TRANSFERABLE",
                          "El DT y el capitán no se transfieren. Nombra otro capitán antes de transferirlo.")


def validate_lineup(entries: list[tuple[int, int]], team_score: int, members: set[int]) -> None:
    """entries: (user_id, goles). Solo miembros, sin repetidos, y goles que no superen el marcador."""
    if not 1 <= len(entries) <= MAX_LINEUP:
        raise DomainError("LINEUP_EMPTY", "Marca entre 1 y 40 jugadores que jugaron el partido.")
    ids = [user_id for user_id, _ in entries]
    if len(set(ids)) != len(ids):
        raise DomainError("LINEUP_DUPLICATE_PLAYER", "Cada jugador va una sola vez en la planilla.")
    if not set(ids) <= members:
        raise DomainError("LINEUP_NOT_A_MEMBER", "Solo puedes poner en la planilla a jugadores de tu equipo.")
    if any(goals < 0 or goals > 999 for _, goals in entries):
        raise DomainError("INVALID_GOALS", "Los goles de cada jugador van de 0 a 999.")
    if sum(goals for _, goals in entries) > team_score:
        raise DomainError("GOALS_EXCEED_SCORE", "La suma de goles supera el marcador de tu equipo.")
