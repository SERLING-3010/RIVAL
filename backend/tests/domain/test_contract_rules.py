from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from app.domain.contract_rules import (
    CostSplit,
    default_terms,
    diff_terms,
    terms_from_dict,
    terms_to_dict,
    validate_terms,
)
from app.domain.errors import DomainError
from app.domain.match_rules import PlaceKind, RefereeMode

NOW = datetime(2026, 11, 23, 15, 0, tzinfo=UTC)


def base():
    return default_terms(NOW + timedelta(days=2), RefereeMode.WITHOUT, PlaceKind.INFORMAL, "Parque")


def code_of(terms) -> str:
    with pytest.raises(DomainError) as error:
        validate_terms(terms, NOW)
    return error.value.code


def test_default_terms_are_valid():
    terms = base()
    validate_terms(terms, NOW)
    assert (terms.field_cost_split, terms.substitutions) == (CostSplit.HALF, None)


@pytest.mark.parametrize(
    ("changes", "code"),
    [
        ({"kickoff_at": NOW - timedelta(minutes=1)}, "KICKOFF_IN_PAST"),
        ({"kickoff_at": NOW + timedelta(days=61)}, "KICKOFF_TOO_FAR"),
        ({"duration_minutes": 10}, "DURATION_OUT_OF_RANGE"),
        ({"duration_minutes": 300}, "DURATION_OUT_OF_RANGE"),
        ({"substitutions": 31}, "SUBSTITUTIONS_OUT_OF_RANGE"),
        ({"cancellation_notice_hours": 73}, "NOTICE_OUT_OF_RANGE"),
        ({"host_kit_color": " azul ", "guest_kit_color": "Azul"}, "KIT_COLORS_CLASH"),
        ({"host_kit_color": ""}, "KIT_COLOR_REQUIRED"),
        ({"referee_mode": RefereeMode.EITHER}, "REFEREE_MODE_REQUIRED"),
        ({"referee_mode": RefereeMode.WITH, "foul_caller_note": "El capitán"}, "FOUL_CALLER_ONLY_WITHOUT_REFEREE"),
    ],
)
def test_invalid_terms_rejected(changes, code):
    assert code_of(replace(base(), **changes)) == code


def test_round_trip_and_diff():
    terms = base()
    changed = replace(terms, duration_minutes=90, host_kit_color="Rojo")
    assert terms_from_dict(terms_to_dict(changed)) == changed
    diff = diff_terms(terms, changed)
    assert diff["before"] == {"duration_minutes": 60, "host_kit_color": "Oscuro"}
    assert diff["after"] == {"duration_minutes": 90, "host_kit_color": "Rojo"}
