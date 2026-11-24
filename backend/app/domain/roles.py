"""Roles de la cuenta (cómo se registra la persona) y roles dentro de un equipo."""

from enum import StrEnum


class UserRole(StrEnum):
    PLAYER = "PLAYER"
    COACH = "COACH"
    REFEREE = "REFEREE"
    VENUE_OWNER = "VENUE_OWNER"


class TeamRole(StrEnum):
    COACH = "COACH"
    CAPTAIN = "CAPTAIN"
    PLAYER = "PLAYER"


ROLES_THAT_CAN_CREATE_TEAMS: frozenset[UserRole] = frozenset({UserRole.PLAYER, UserRole.COACH})
