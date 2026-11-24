import pytest

from app.domain.errors import DomainError
from app.domain.roles import TeamRole, UserRole
from app.domain.team_rules import (
    MemberView,
    check_can_leave,
    initial_team_role,
    resolve_admin,
)


def members(*pairs: tuple[int, TeamRole]) -> list[MemberView]:
    return [MemberView(user_id=uid, role=role) for uid, role in pairs]


def test_coach_creator_becomes_coach():
    assert initial_team_role(UserRole.COACH) == TeamRole.COACH


def test_player_creator_becomes_captain():
    assert initial_team_role(UserRole.PLAYER) == TeamRole.CAPTAIN


def test_admin_is_coach_when_present():
    roster = members((1, TeamRole.CAPTAIN), (2, TeamRole.COACH), (3, TeamRole.PLAYER))
    assert resolve_admin(roster) == 2


def test_admin_falls_back_to_captain():
    roster = members((1, TeamRole.PLAYER), (2, TeamRole.CAPTAIN))
    assert resolve_admin(roster) == 2


def test_no_admin_without_coach_or_captain():
    assert resolve_admin(members((1, TeamRole.PLAYER))) is None


def test_coach_cannot_leave_without_captain():
    roster = members((1, TeamRole.COACH), (2, TeamRole.PLAYER))
    with pytest.raises(DomainError) as error:
        check_can_leave(1, roster)
    assert error.value.code == "ADMIN_SUCCESSOR_REQUIRED"


def test_coach_can_leave_when_captain_exists():
    roster = members((1, TeamRole.COACH), (2, TeamRole.CAPTAIN))
    check_can_leave(1, roster)


def test_captain_admin_cannot_leave_with_teammates():
    roster = members((1, TeamRole.CAPTAIN), (2, TeamRole.PLAYER))
    with pytest.raises(DomainError) as error:
        check_can_leave(1, roster)
    assert error.value.code == "ADMIN_SUCCESSOR_REQUIRED"


def test_last_member_can_leave():
    check_can_leave(1, members((1, TeamRole.CAPTAIN)))


def test_player_can_always_leave():
    roster = members((1, TeamRole.COACH), (2, TeamRole.PLAYER))
    check_can_leave(2, roster)


def test_non_member_cannot_leave():
    with pytest.raises(DomainError) as error:
        check_can_leave(9, members((1, TeamRole.COACH)))
    assert error.value.code == "NOT_A_MEMBER"
