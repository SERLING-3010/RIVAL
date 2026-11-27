from datetime import UTC, datetime, timedelta

import pytest

from app.domain.errors import DomainError
from app.domain.fixture_rules import round_dates, round_robin
from app.domain.standings_rules import MatchScore, standings

NOW = datetime(2026, 11, 24, 15, 0, tzinfo=UTC)


def test_round_robin_even_everyone_plays_everyone_once():
    rounds = round_robin([1, 2, 3, 4])
    assert len(rounds) == 3 and all(len(r) == 2 for r in rounds)
    pairs = {frozenset(p) for r in rounds for p in r}
    assert len(pairs) == 6  # C(4,2): todos contra todos, sin repetir
    for r in rounds:  # nadie juega dos veces en la misma fecha
        teams = [t for p in r for t in p]
        assert len(teams) == len(set(teams))


def test_round_robin_odd_has_a_rest_each_round():
    rounds = round_robin([1, 2, 3])
    assert len(rounds) == 3 and all(len(r) == 1 for r in rounds)
    assert {frozenset(p) for r in rounds for p in r} == {frozenset({1, 2}), frozenset({1, 3}), frozenset({2, 3})}


def test_round_robin_needs_two_teams():
    with pytest.raises(DomainError) as error:
        round_robin([1])
    assert error.value.code == "FIXTURE_NEEDS_TEAMS"


def test_round_dates_and_limits():
    first = NOW + timedelta(days=2)
    assert round_dates(first, 7, 3, NOW) == [first, first + timedelta(days=7), first + timedelta(days=14)]
    with pytest.raises(DomainError) as long:
        round_dates(first, 14, 6, NOW)
    assert long.value.code == "FIXTURE_TOO_LONG"
    with pytest.raises(DomainError) as past:
        round_dates(NOW - timedelta(hours=1), 7, 2, NOW)
    assert past.value.code == "FIXTURE_IN_PAST"
    with pytest.raises(DomainError) as gap:
        round_dates(first, 0, 2, NOW)
    assert gap.value.code == "FIXTURE_GAP_OUT_OF_RANGE"


def test_standings_points_and_tiebreaks():
    names = {1: "Águilas", 2: "Bravos", 3: "Cóndores"}
    table = standings(names, [MatchScore(1, 2, 2, 0), MatchScore(2, 3, 1, 1), MatchScore(3, 1, 3, 1)])
    rows = [(r.team_id, r.played, r.points, r.goal_difference) for r in table]
    assert rows == [(3, 2, 4, 2), (1, 2, 3, 0), (2, 2, 1, -2)]
    assert standings(names, [])[0].played == 0  # sin partidos todos en cero, por nombre
    assert [r.team_id for r in standings(names, [])] == [1, 2, 3]
