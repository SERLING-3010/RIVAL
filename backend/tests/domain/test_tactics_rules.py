import pytest

from app.domain import tactics_rules
from app.domain.errors import DomainError

ELIGIBLE = set(range(1, 10))
SEVEN = [(i, "Defensa") for i in range(1, 8)]


def test_formation_sums_outfield_players_only_in_football():
    assert tactics_rules.validate_formation("FOOTBALL", 7, " 2-3-1 ") == "2-3-1"
    assert tactics_rules.validate_formation("FOOTBALL", 11, "4-4-2") == "4-4-2"
    assert tactics_rules.validate_formation("FOOTBALL", 7, None) is None
    for bad in ("3-3-1", "2-3", "0-3-3", "2--4", "abc"):
        with pytest.raises(DomainError):
            tactics_rules.validate_formation("FOOTBALL", 7, bad)
    assert tactics_rules.validate_formation("BASKETBALL", 5, None) is None
    with pytest.raises(DomainError):
        tactics_rules.validate_formation("BASKETBALL", 5, "2-2")


def test_suggested_formations_are_valid_for_their_modality():
    sizes = {"F5": 5, "MICRO5": 5, "F7": 7, "F8": 8, "F11": 11}
    for modality, per_side in sizes.items():
        for formation in tactics_rules.suggested_formations(modality):
            assert tactics_rules.validate_formation("FOOTBALL", per_side, formation) == formation
    assert tactics_rules.suggested_formations("B5X5") == []


def test_slots_rules():
    assert tactics_rules.validate_slots([(1, "  Arquero ")] + SEVEN[1:], [8], 7, ELIGIBLE)[0] == (1, "Arquero")
    cases = [
        (SEVEN[:6], []),  # faltan titulares
        (SEVEN, [1]),  # repetido
        (SEVEN, [42]),  # no convocado
        ([(1, "")] + SEVEN[1:], []),  # sin posición
        (SEVEN, list(range(20, 33))),  # demasiados suplentes
    ]
    for starters, subs in cases:
        with pytest.raises(DomainError):
            tactics_rules.validate_slots(starters, subs, 7, ELIGIBLE | set(range(20, 33)) - {42})
