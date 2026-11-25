"""Copa eliminatoria de una liga (Sprint 16): cuadro sembrado, pases directos y avance del ganador.

Siembra clásica: el 1 juega contra el último, y los mejores sembrados solo se cruzan al final.
Si los equipos no llenan una potencia de 2, los mejores sembrados pasan directo la primera ronda.
"""

from app.domain.errors import DomainError

MIN_TEAMS, MAX_TEAMS = 2, 32
Slot = int | None  # equipo, o None si es un pase directo


def bracket_size(teams: int) -> int:
    if not MIN_TEAMS <= teams <= MAX_TEAMS:
        raise DomainError("CUP_TEAM_COUNT", f"La copa necesita de {MIN_TEAMS} a {MAX_TEAMS} equipos aprobados.")
    size = 2
    while size < teams:
        size *= 2
    return size


def rounds_for(size: int) -> int:
    return size.bit_length() - 1


def seed_positions(size: int) -> list[int]:
    """Sembrado (1 = el mejor) en cada posición del cuadro: para 8, [1, 8, 4, 5, 2, 7, 3, 6]."""
    order = [1]
    while len(order) < size:
        total = len(order) * 2 + 1
        order = [s for seed in order for s in (seed, total - seed)]
    return order


def first_round(seeded_team_ids: list[int]) -> list[tuple[Slot, Slot]]:
    """Cruces de la primera ronda; None donde el rival es un pase directo."""
    size = bracket_size(len(seeded_team_ids))
    slots: list[Slot] = [seeded_team_ids[s - 1] if s <= len(seeded_team_ids) else None for s in seed_positions(size)]
    return [(slots[i], slots[i + 1]) for i in range(0, size, 2)]


def match_winner(host_id: int, guest_id: int, host_goals: int, guest_goals: int,
                 tiebreak_winner: int | None) -> int | None:
    """Ganador del cruce; con empate, el definido por penales, o None si aún no se definió."""
    if host_goals != guest_goals:
        return host_id if host_goals > guest_goals else guest_id
    return tiebreak_winner


def round_name(round_number: int, total_rounds: int) -> str:
    left = total_rounds - round_number
    names = {0: "Final", 1: "Semifinal", 2: "Cuartos de final", 3: "Octavos de final"}
    return names.get(left, f"Ronda {round_number}")
