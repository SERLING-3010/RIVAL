import pytest

from app.domain.errors import DomainError
from app.domain.special_cards import CODES, Feats, best, needs_city_rank, progress, validate_kinds


def _reached(feats: Feats, card_media: int) -> set[str]:
    return {p.code for p in progress(feats) if p.reached(card_media)}


def test_fifteen_specials_from_rubi_to_elite():
    assert len(CODES) == 15 and CODES[0] == "RUBI" and CODES[-1] == "ELITE"


def test_a_special_needs_both_the_media_and_the_feat():
    assert "RUBI" not in _reached(Feats(goals=10), 74)  # hazaña sí, media no
    assert "RUBI" not in _reached(Feats(goals=9), 90)  # media sí, hazaña no
    assert "RUBI" in _reached(Feats(goals=10), 75)


def test_feats_from_match_records_and_confirmed_goal_kinds():
    feats = Feats(goals=30, hat_tricks=3, pokers=1, manitas=1, kinds={"CHILENA": 1, "TIRO_LIBRE": 2})
    assert _reached(feats, 82) == {"RUBI", "ESMERALDA", "DIAMANTE", "PADPARADSCHA", "ALEJANDRITA", "SERENDIBITA"}
    rubi = progress(Feats(goals=7))[0]
    assert [(g.label, g.current, g.target, g.done) for g in rubi.goals] == [("10 goles", 7, 10, False)]


def test_red_diamond_needs_every_feat():
    almost = Feats(goals=100, kinds={"CHILENA": 1})
    assert "DIAMANTE_ROJO" not in _reached(almost, 99)
    assert "DIAMANTE_ROJO" in _reached(Feats(goals=100, kinds={"CHILENA": 1, "OLIMPICO": 1}), 86)


def test_goal_types_count_normal_goals_as_one_more_type():
    assert Feats(goals=4, kinds={"CABEZA": 1, "PENAL": 1, "CHILENA": 1, "OLIMPICO": 1}).goal_types() == 4
    assert Feats(goals=5, kinds={"CABEZA": 1, "PENAL": 1, "CHILENA": 1, "OLIMPICO": 1}).goal_types() == 5


def test_cup_and_city_feats():
    assert "CORONA" in _reached(Feats(cup_champion=True), 87)
    assert "ELITE" in _reached(Feats(city_rank=3), 92)
    assert "ELITE" not in _reached(Feats(city_rank=4), 99)
    assert needs_city_rank(92) and not needs_city_rank(91)


def test_best_is_the_hardest_owned():
    assert best({"RUBI", "DIAMANTE", "ESMERALDA"}) == "DIAMANTE"
    assert best(set()) is None


def test_goal_kinds_must_be_known_and_not_exceed_goals():
    validate_kinds(2, ["CHILENA", "CABEZA"])
    with pytest.raises(DomainError) as unknown:
        validate_kinds(1, ["TACON"])
    assert unknown.value.code == "INVALID_GOAL_KIND"
    with pytest.raises(DomainError) as too_many:
        validate_kinds(1, ["CHILENA", "PENAL"])
    assert too_many.value.code == "GOAL_KINDS_EXCEED_GOALS"
