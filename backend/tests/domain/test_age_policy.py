from datetime import date

from app.domain.age_policy import MIN_AGE_YEARS, is_adult


def test_min_age_is_18():
    assert MIN_AGE_YEARS == 18


def test_is_adult_turns_18_on_birthday():
    assert is_adult(date(2008, 11, 23), today=date(2026, 11, 23)) is True


def test_is_not_adult_day_before_birthday():
    assert is_adult(date(2008, 11, 24), today=date(2026, 11, 23)) is False


def test_leap_day_birthday_not_adult_on_feb_28():
    assert is_adult(date(2008, 2, 29), today=date(2026, 2, 28)) is False


def test_leap_day_birthday_adult_on_march_first():
    assert is_adult(date(2008, 2, 29), today=date(2026, 3, 1)) is True


def test_future_birth_date_is_not_adult():
    assert is_adult(date(2030, 1, 1), today=date(2026, 11, 23)) is False
