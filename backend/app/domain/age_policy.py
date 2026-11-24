"""Política de edad: RIVAL es solo para mayores de 18 (decisión del dueño, 23/11/2026)."""

from datetime import date

MIN_AGE_YEARS = 18


def _birthday_in_year(birth_date: date, year: int) -> date:
    """Cumpleaños en un año dado. Un 29 de febrero cumple el 1 de marzo en años no bisiestos.

    [SUPUESTO] Regla conservadora: nadie se considera adulto antes de tiempo.
    """
    try:
        return birth_date.replace(year=year)
    except ValueError:
        return date(year, 3, 1)


def is_adult(birth_date: date, today: date) -> bool:
    """True si la persona ya cumplió MIN_AGE_YEARS en la fecha `today`."""
    if birth_date > today:
        return False
    coming_of_age = _birthday_in_year(birth_date, birth_date.year + MIN_AGE_YEARS)
    return today >= coming_of_age
