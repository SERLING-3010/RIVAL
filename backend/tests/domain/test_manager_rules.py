import pytest

from app.domain.errors import ConflictError, DomainError
from app.domain.manager_rules import (
    check_balance,
    check_transferable,
    result_rewards,
    validate_lineup,
    validate_offer_amount,
)
from app.domain.roles import TeamRole


def test_rewards_for_win_draw_and_loss():
    assert result_rewards(3, 1) == (150, 50)
    assert result_rewards(0, 2) == (50, 150)
    assert result_rewards(1, 1) == (75, 75)


def test_offer_amount_and_balance():
    validate_offer_amount(1)
    for bad in (0, -5, 1_000_001):
        with pytest.raises(DomainError) as error:
            validate_offer_amount(bad)
        assert error.value.code == "INVALID_OFFER_AMOUNT"
    check_balance(100, 100)
    with pytest.raises(ConflictError) as poor:
        check_balance(99, 100)
    assert poor.value.code == "INSUFFICIENT_COINS"


def test_only_plain_players_are_transferable():
    check_transferable(TeamRole.PLAYER)
    for role in (TeamRole.COACH, TeamRole.CAPTAIN):
        with pytest.raises(DomainError) as error:
            check_transferable(role)
        assert error.value.code == "NOT_TRANSFERABLE"


def test_lineup_rules():
    validate_lineup([(1, 2), (2, 0)], team_score=2, members={1, 2, 3})
    cases = [
        ([], 0, "LINEUP_EMPTY"),
        ([(1, 1), (1, 0)], 1, "LINEUP_DUPLICATE_PLAYER"),
        ([(9, 0)], 0, "LINEUP_NOT_A_MEMBER"),
        ([(1, -1)], 0, "INVALID_GOALS"),
        ([(1, 2), (2, 1)], 2, "GOALS_EXCEED_SCORE"),
    ]
    for entries, score, code in cases:
        with pytest.raises(DomainError) as error:
            validate_lineup(entries, team_score=score, members={1, 2, 3})
        assert error.value.code == code
