from datetime import UTC, datetime, timedelta

import pytest

from app.domain.errors import DomainError
from app.domain.matchday_rules import check_before_kickoff, check_can_rate, validate_score

KICKOFF = datetime(2026, 11, 28, 20, 0, tzinfo=UTC)


def code(fn, *args):
    with pytest.raises(DomainError) as error:
        fn(*args)
    return error.value.code


def test_callup_closes_at_kickoff():
    check_before_kickoff(KICKOFF, KICKOFF - timedelta(minutes=1))
    assert code(check_before_kickoff, KICKOFF, KICKOFF) == "MATCH_ALREADY_STARTED"


def test_score_range():
    validate_score(1)
    validate_score(10)
    assert code(validate_score, 0) == "INVALID_PLAYER_SCORE"
    assert code(validate_score, 11) == "INVALID_PLAYER_SCORE"


def test_who_can_be_rated_and_until_when():
    later = KICKOFF + timedelta(days=1)
    check_can_rate(1, 2, {2, 3}, KICKOFF, later)
    assert code(check_can_rate, 2, 2, {2}, KICKOFF, later) == "CANNOT_RATE_SELF"
    assert code(check_can_rate, 1, 9, {2}, KICKOFF, later) == "PLAYER_NOT_IN_LINEUP"
    assert code(check_can_rate, 1, 2, {2}, KICKOFF, KICKOFF + timedelta(days=8)) == "RATING_WINDOW_CLOSED"
