from datetime import UTC, datetime, timedelta

from app.domain.geo import DistanceBand
from app.domain.suggestion_rules import Signals, favorite_day, score, worth_suggesting

SAT_EVENING = datetime(2026, 11, 28, 23, 0, tzinfo=UTC)  # sábado 18:00 en Colombia
SUN_EARLY_UTC = datetime(2026, 11, 29, 3, 0, tzinfo=UTC)  # todavía sábado 22:00 en Colombia


def signals(**over) -> Signals:
    base = {"distance_band": None, "my_level": None, "their_level": None, "my_days": [], "their_days": [],
            "played_recently": False}
    return Signals(**{**base, **over})


def test_favorite_day_uses_local_time():
    assert favorite_day([SAT_EVENING, SUN_EARLY_UTC, SAT_EVENING + timedelta(days=1)]) == 5  # sábado
    assert favorite_day([]) is None


def test_reasons_explain_every_point():
    points, reasons = score(signals(distance_band=DistanceBand.UNDER_2_KM, my_level=1520, their_level=1480,
                                    my_days=[SAT_EVENING], their_days=[SAT_EVENING + timedelta(days=7)]))
    assert points == 9
    assert reasons == ["Está a menos de 2 km", "Su nivel es parecido al tuyo", "También juega los sábados",
                       "No se han enfrentado en el último mes"]


def test_never_exact_distance_and_far_levels_add_nothing():
    points, reasons = score(signals(distance_band=DistanceBand.OVER_5_KM, my_level=1300, their_level=1800))
    assert (points, reasons) == (1, ["No se han enfrentado en el último mes"])
    assert not worth_suggesting(points, reasons)
    assert not any("km" in r and r[0].isdigit() for r in reasons)


def test_recent_or_scheduled_rival_is_not_suggested():
    points, reasons = score(signals(distance_band=DistanceBand.UNDER_2_KM, played_recently=True,
                                    my_days=[SAT_EVENING], their_days=[SAT_EVENING]))
    assert (points, reasons) == (0, [])
    assert not worth_suggesting(points, reasons)
