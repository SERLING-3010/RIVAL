from datetime import UTC, datetime, timedelta

import pytest

from app.domain.errors import DomainError
from app.domain.match_rules import RefereeMode, check_offer_referee, check_proposed_start, validate_window

NOW = datetime(2026, 11, 23, 15, 0, tzinfo=UTC)


def test_valid_window():
    validate_window(NOW + timedelta(days=1), NOW + timedelta(days=3), NOW)


@pytest.mark.parametrize(
    ("start", "end", "code"),
    [
        (NOW - timedelta(hours=1), NOW + timedelta(days=1), "WINDOW_IN_PAST"),
        (NOW + timedelta(days=2), NOW + timedelta(days=1), "WINDOW_INVERTED"),
        (NOW + timedelta(days=1), NOW + timedelta(days=16), "WINDOW_TOO_LONG"),
        (NOW + timedelta(days=61), NOW + timedelta(days=62), "WINDOW_TOO_FAR"),
    ],
)
def test_invalid_windows(start, end, code):
    with pytest.raises(DomainError) as error:
        validate_window(start, end, NOW)
    assert error.value.code == code


def test_proposed_start_must_fall_inside_window():
    start, end = NOW + timedelta(days=1), NOW + timedelta(days=2)
    check_proposed_start(start, start, end, NOW)
    check_proposed_start(end, start, end, NOW)
    with pytest.raises(DomainError) as error:
        check_proposed_start(end + timedelta(minutes=1), start, end, NOW)
    assert error.value.code == "OFFER_OUTSIDE_WINDOW"
    with pytest.raises(DomainError) as past:
        check_proposed_start(start, start, end, start + timedelta(hours=1))
    assert past.value.code == "OFFER_IN_PAST"


def test_offer_must_choose_concrete_referee_mode_compatible_with_request():
    check_offer_referee(RefereeMode.EITHER, RefereeMode.WITHOUT)
    check_offer_referee(RefereeMode.WITH, RefereeMode.WITH)
    with pytest.raises(DomainError):
        check_offer_referee(RefereeMode.WITH, RefereeMode.WITHOUT)
    with pytest.raises(DomainError):
        check_offer_referee(RefereeMode.EITHER, RefereeMode.EITHER)
