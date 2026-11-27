from datetime import UTC, datetime, timedelta

from app.domain.achievement_rules import Outcome, PlayedMatch, outcome, player_badges, team_badges

T0 = datetime(2026, 11, 1, tzinfo=UTC)


def day(n: int) -> datetime:
    return T0 + timedelta(days=n)


def by_code(badges):
    return {b.code: b for b in badges}


def test_player_badges_have_the_date_they_were_completed_or_progress():
    matches = [PlayedMatch(day(n), Outcome.WIN, goals=3 if n == 2 else 1) for n in range(1, 11)]
    got = by_code(player_badges(matches, check_ins=[day(1), day(2)], cup_titles=[]))
    assert got["DEBUT"].earned_at == day(1)
    assert got["HAT_TRICK"].earned_at == day(2)
    assert (got["MATCHES_10"].earned_at, got["WINS_10"].earned_at) == (day(10), day(10))
    assert got["GOALS_10"].earned_at == day(8)  # 1 + 3 + 1×6 = 10 en el octavo partido
    assert (got["MATCHES_50"].earned_at, got["MATCHES_50"].progress) == (None, "10/50")
    assert (got["PUNCTUAL"].earned_at, got["PUNCTUAL"].progress) == (None, "2/5")
    assert got["CUP_CHAMPION"].progress == "0/1"


def test_order_does_not_depend_on_input_order():
    late, early = PlayedMatch(day(5), Outcome.LOSS), PlayedMatch(day(1), Outcome.WIN)
    assert by_code(team_badges([late, early], []))["FIRST_WIN"].earned_at == day(1)


def test_unbeaten_streak_resets_on_a_loss():
    seq = [Outcome.WIN, Outcome.DRAW, Outcome.WIN, Outcome.LOSS] + [Outcome.DRAW] * 4
    matches = [PlayedMatch(day(i), o) for i, o in enumerate(seq)]
    assert by_code(team_badges(matches, []))["UNBEATEN_5"].progress == "4/5"
    matches.append(PlayedMatch(day(20), Outcome.WIN))
    assert by_code(team_badges(matches, [day(21)]))["UNBEATEN_5"].earned_at == day(20)
    assert by_code(team_badges(matches, [day(21)]))["CUP_CHAMPION"].earned_at == day(21)


def test_outcome():
    assert [outcome(2, 1), outcome(1, 1), outcome(0, 3)] == [Outcome.WIN, Outcome.DRAW, Outcome.LOSS]
