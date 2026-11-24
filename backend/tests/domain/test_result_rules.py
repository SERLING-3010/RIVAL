from datetime import UTC, datetime, timedelta

import pytest

from app.domain.errors import DomainError
from app.domain.result_rules import ResultStatus, check_can_report, resolve_result, validate_score

KICKOFF = datetime(2026, 11, 25, 1, 0, tzinfo=UTC)


def test_cannot_report_before_kickoff():
    with pytest.raises(DomainError) as early:
        check_can_report(KICKOFF, KICKOFF - timedelta(minutes=1))
    assert early.value.code == "RESULT_TOO_EARLY"
    check_can_report(KICKOFF, KICKOFF)


@pytest.mark.parametrize("score", [(-1, 0), (0, 1000)])
def test_score_out_of_range(score):
    with pytest.raises(DomainError) as error:
        validate_score(*score)
    assert error.value.code == "SCORE_OUT_OF_RANGE"


def test_resolution():
    assert resolve_result([]) == (ResultStatus.PENDING, None)
    assert resolve_result([(2, 1)]) == (ResultStatus.PENDING, None)
    assert resolve_result([(2, 1), (2, 1)]) == (ResultStatus.CONFIRMED, (2, 1))
    assert resolve_result([(2, 1), (1, 2)]) == (ResultStatus.DISPUTED, None)
