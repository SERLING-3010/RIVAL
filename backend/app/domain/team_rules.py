"""Reglas de administración de equipos.

El administrador no se guarda: se calcula. Es el DT si existe; si no, el capitán.
Así el equipo nunca puede quedar con dos administradores.
"""

from dataclasses import dataclass

from app.domain.errors import DomainError
from app.domain.roles import TeamRole, UserRole


@dataclass(frozen=True)
class MemberView:
    user_id: int
    role: TeamRole


def initial_team_role(creator_role: UserRole) -> TeamRole:
    """Quien crea el equipo: el DT entra como DT; cualquier otro, como capitán."""
    return TeamRole.COACH if creator_role == UserRole.COACH else TeamRole.CAPTAIN


def resolve_admin(members: list[MemberView]) -> int | None:
    """Devuelve el user_id del administrador activo, o None si no hay DT ni capitán."""
    for wanted in (TeamRole.COACH, TeamRole.CAPTAIN):
        for member in members:
            if member.role == wanted:
                return member.user_id
    return None


def check_can_leave(user_id: int, members: list[MemberView]) -> None:
    """Impide que el equipo quede sin administrador cuando todavía tiene jugadores."""
    if not any(m.user_id == user_id for m in members):
        raise DomainError("NOT_A_MEMBER", "No perteneces a este equipo.")
    remaining = [m for m in members if m.user_id != user_id]
    if not remaining:
        return
    if resolve_admin(members) != user_id:
        return
    if resolve_admin(remaining) is None:
        raise DomainError(
            "ADMIN_SUCCESSOR_REQUIRED",
            "Antes de salir, nombra un capitán para que el equipo no quede sin administrador.",
        )
