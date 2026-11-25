import pytest

from app.domain import cup_rules
from app.domain.errors import DomainError


def test_bracket_size_and_rounds():
    assert [cup_rules.bracket_size(n) for n in (2, 3, 5, 8, 9, 32)] == [2, 4, 8, 8, 16, 32]
    assert [cup_rules.rounds_for(s) for s in (2, 4, 8, 32)] == [1, 2, 3, 5]
    for bad in (1, 33):
        with pytest.raises(DomainError):
            cup_rules.bracket_size(bad)


def test_classic_seeding_keeps_top_seeds_apart():
    assert cup_rules.seed_positions(8) == [1, 8, 4, 5, 2, 7, 3, 6]
    assert sorted(cup_rules.seed_positions(16)) == list(range(1, 17))


def test_first_round_gives_byes_to_best_seeds():
    teams = [10, 20, 30, 40, 50]  # ya sembrados: 10 es el mejor
    assert cup_rules.first_round(teams) == [(10, None), (40, 50), (20, None), (30, None)]


def test_winner_and_round_names():
    assert cup_rules.match_winner(1, 2, 3, 1, None) == 1
    assert cup_rules.match_winner(1, 2, 0, 2, None) == 2
    assert cup_rules.match_winner(1, 2, 1, 1, None) is None
    assert cup_rules.match_winner(1, 2, 1, 1, 2) == 2
    assert [cup_rules.round_name(r, 5) for r in range(1, 6)] == [
        "Ronda 1", "Octavos de final", "Cuartos de final", "Semifinal", "Final"]
