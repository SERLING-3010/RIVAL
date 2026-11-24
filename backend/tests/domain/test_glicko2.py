import pytest

from app.domain.glicko2 import GameResult, Rating, update


def test_glickman_paper_example():
    """Ejemplo del artículo "Example of the Glicko-2 system" (Glickman, 2013)."""
    player = Rating(rating=1500, rd=200, volatility=0.06)
    games = [
        GameResult(Rating(1400, 30, 0.06), 1.0),
        GameResult(Rating(1550, 100, 0.06), 0.0),
        GameResult(Rating(1700, 300, 0.06), 0.0),
    ]
    new = update(player, games)
    assert new.rating == pytest.approx(1464.06, abs=0.05)
    assert new.rd == pytest.approx(151.52, abs=0.05)
    assert new.volatility == pytest.approx(0.05999, abs=0.00001)


def test_new_teams_move_a_lot_and_become_more_certain():
    new_team = Rating()
    after_win = update(new_team, [GameResult(Rating(), 1.0)])
    after_loss = update(new_team, [GameResult(Rating(), 0.0)])
    assert after_win.rating > 1600 and after_loss.rating < 1400
    assert after_win.rd < new_team.rd


def test_draw_between_equals_keeps_rating():
    new = update(Rating(), [GameResult(Rating(), 0.5)])
    assert new.rating == pytest.approx(1500, abs=0.001)


def test_no_games_only_increases_uncertainty():
    new = update(Rating(1600, 80, 0.06), [])
    assert new.rating == 1600 and new.rd > 80
