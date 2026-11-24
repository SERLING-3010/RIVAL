from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.domain.errors import DomainError
from app.domain.venue_rules import (
    check_slot_covers_match,
    slots_overlap,
    validate_address,
    validate_reference_price,
    validate_slot,
)

NOW = datetime(2026, 11, 24, 15, 0, tzinfo=UTC)


def code(fn, *args) -> str:
    with pytest.raises(DomainError) as error:
        fn(*args)
    return error.value.code


def test_slot_rules():
    start = NOW + timedelta(days=1)
    validate_slot(start, start + timedelta(minutes=90), NOW)
    assert code(validate_slot, NOW - timedelta(minutes=1), NOW + timedelta(hours=1), NOW) == "SLOT_IN_PAST"
    assert code(validate_slot, start, start + timedelta(minutes=20), NOW) == "SLOT_DURATION_OUT_OF_RANGE"
    assert code(validate_slot, start, start + timedelta(minutes=300), NOW) == "SLOT_DURATION_OUT_OF_RANGE"
    far = NOW + timedelta(days=61)
    assert code(validate_slot, far, far + timedelta(hours=1), NOW) == "SLOT_TOO_FAR"


def test_overlap_is_half_open():
    a = (NOW, NOW + timedelta(hours=1))
    assert slots_overlap(a, (NOW + timedelta(minutes=30), NOW + timedelta(hours=2)))
    assert not slots_overlap(a, (NOW + timedelta(hours=1), NOW + timedelta(hours=2)))


def test_slot_must_cover_whole_match():
    slot = (NOW, NOW + timedelta(hours=2))
    check_slot_covers_match(slot, NOW + timedelta(minutes=30), 90)
    assert code(check_slot_covers_match, slot, NOW + timedelta(minutes=31), 90) == "SLOT_DOES_NOT_COVER_MATCH"
    assert code(check_slot_covers_match, slot, NOW - timedelta(minutes=1), 60) == "SLOT_DOES_NOT_COVER_MATCH"


def test_price_and_address():
    assert validate_reference_price(Decimal("80000")) == Decimal("80000.00")
    assert validate_reference_price(None) is None
    assert code(validate_reference_price, Decimal("-1")) == "INVALID_REFERENCE_PRICE"
    assert code(validate_reference_price, Decimal("10.555")) == "INVALID_REFERENCE_PRICE"
    assert validate_address("  Calle 72 # 45-10 ") == "Calle 72 # 45-10"
    assert code(validate_address, "x") == "INVALID_ADDRESS"
