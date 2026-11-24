import pytest

from app.domain.errors import DomainError, PermissionDeniedError
from app.domain.league_rules import (
    StaffRole,
    check_can_create,
    check_can_decide,
    validate_league_name,
    validate_season,
)


def test_name_and_season():
    assert validate_league_name("  Liga del Prado ") == "Liga del Prado"
    for bad in ("ab", "x" * 61):
        with pytest.raises(DomainError):
            validate_league_name(bad)
    assert validate_season("2026-2") == "2026-2"
    assert validate_season(" 2027 ") == "2027"
    for bad in ("2026-3", "26", "verano"):
        with pytest.raises(DomainError) as error:
            validate_season(bad)
        assert error.value.code == "INVALID_SEASON"


def test_who_can_create():
    check_can_create(is_referee=True, has_team=False)
    check_can_create(is_referee=False, has_team=True)
    with pytest.raises(PermissionDeniedError) as error:
        check_can_create(is_referee=False, has_team=False)
    assert error.value.code == "LEAGUE_CREATOR_NOT_ALLOWED"


@pytest.mark.parametrize(
    ("role", "kind", "allowed"),
    [
        (StaffRole.ORGANIZER, "team", True),
        (StaffRole.CO_ORGANIZER, "team", True),
        (StaffRole.REFEREE_COORDINATOR, "team", False),
        (StaffRole.REFEREE_COORDINATOR, "referee", True),
        (None, "referee", False),
    ],
)
def test_who_decides(role, kind, allowed):
    if allowed:
        check_can_decide(role, kind)
    else:
        with pytest.raises(PermissionDeniedError):
            check_can_decide(role, kind)
