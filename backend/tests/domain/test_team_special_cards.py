from app.domain.special_cards import CODES
from app.domain.team_special_cards import TEAM_SPECIALS, TeamFeats, feats_from_scores, needs_city_rank, progress


def _reached(feats: TeamFeats, media: int) -> set[str]:
    return {p.code for p in progress(feats) if p.reached(media)}


def test_same_fifteen_codes_as_player_specials():
    assert [code for code, _m, _r in TEAM_SPECIALS] == CODES


def test_feats_from_confirmed_scores():
    f = feats_from_scores([(2, 0), (6, 1), (3, 2), (1, 1), (0, 2), (4, 0)], cups=1)
    assert (f.wins, f.goals, f.clean_sheets, f.goleadas) == (4, 16, 2, 1)
    assert (f.best_win_streak, f.best_unbeaten_streak, f.cups) == (3, 4, 1)


def test_team_special_needs_media_and_feat():
    ten_wins = feats_from_scores([(1, 0)] * 10)
    assert "RUBI" not in _reached(ten_wins, 74)
    assert {"RUBI", "DIAMANTE", "GRANDIDIERITA", "ALEJANDRITA", "SERENDIBITA"} <= _reached(ten_wins, 82)
    assert "PRISMA" in _reached(TeamFeats(leagues=1), 88)
    assert "GALAXIA" not in _reached(TeamFeats(leagues=1, cups=1), 99)  # el doblete es de la misma liga
    assert "GALAXIA" in _reached(TeamFeats(doubles=1), 90)
    assert "ELITE" in _reached(TeamFeats(city_rank=2), 92) and needs_city_rank(92) and not needs_city_rank(91)
