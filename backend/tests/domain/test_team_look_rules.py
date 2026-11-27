import pytest

from app.domain.errors import DomainError
from app.domain.team_look_rules import BASIC, available_designs, check_choice, parse_crest, shown_design


def test_crest_is_built_from_rival_pieces():
    crest = parse_crest("ESCUDO|#0B6B3A|#F6DE92|ESTRELLA")
    assert (crest.shape, crest.symbol, crest.encode()) == ("ESCUDO", "ESTRELLA", "ESCUDO|#0B6B3A|#F6DE92|ESTRELLA")
    for bad in ("ESCUDO|#0B6B3A|#F6DE92", "TRIANGULO|#0B6B3A|#F6DE92|RAYO", "ESCUDO|#123456|#F6DE92|RAYO",
                "ESCUDO|#0B6B3A|#0B6B3A|RAYO"):
        with pytest.raises(DomainError) as error:
            parse_crest(bad)
        assert error.value.code == "INVALID_CREST"


def test_design_choice_only_among_owned():
    owned = ["RUBI", "DIAMANTE"]
    assert available_designs(owned) == [BASIC, "RUBI", "DIAMANTE"]
    check_choice("RUBI", owned)
    check_choice(None, owned)
    with pytest.raises(DomainError) as error:
        check_choice("ELITE", owned)
    assert error.value.code == "DESIGN_NOT_OWNED"


def test_shown_design():
    assert shown_design(None, ["RUBI", "DIAMANTE"], "ORO", "DIAMANTE") == "DIAMANTE"  # sin elección: la mejor
    assert shown_design("RUBI", ["RUBI", "DIAMANTE"], "ORO", "DIAMANTE") == "RUBI"
    assert shown_design(BASIC, ["RUBI"], "PLATA", "RUBI") == "PLATA"
    assert shown_design(None, [], "BRONCE", None) == "BRONCE"
