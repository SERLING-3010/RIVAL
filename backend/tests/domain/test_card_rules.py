from app.domain.card_rules import market_value, media, tier


def test_media_starts_neutral_and_grows_only_by_playing():
    assert media(0, 0, 0, None, 0) == 57  # 40 + 5,5 × 3 = 56,5, sube a 57
    assert media(1, 1, 3, None, 0) == 71  # 40 + 16,5 + 0,3 + 10 + 4
    assert media(50, 50, 80, 10.0, 30) == 99  # tope
    assert media(50, 50, 80, 10.0, 2) == 86  # menos de 3 votos: valoración neutral (85,5 sube a 86)
    assert media(0, 0, 0, 6.0, 3) == 58  # 40 + 18


def test_bad_ratings_lower_the_media():
    assert media(20, 10, 5, 3.0, 8) < media(20, 10, 5, 8.0, 8)


def test_basic_card_comes_only_from_the_media():
    assert (tier(57).name, tier(57).rank, tier(57).next_name, tier(57).media_to_next) == ("BRONCE", 1, "PLATA", 8)
    assert (tier(64).name, tier(65).name) == ("BRONCE", "PLATA")
    assert (tier(74).name, tier(74).media_to_next) == ("PLATA", 1)
    assert (tier(75).name, tier(79).name, tier(79).next_name) == ("ORO", "ORO", "ORO_BRILLANTE")
    top = tier(80)
    assert (top.name, top.rank, top.next_name, top.media_to_next) == ("ORO_BRILLANTE", 4, None, 0)


def test_market_value_grows_with_media_card_specials_and_form():
    assert market_value(57, 1, 0, []) == 290  # 285 redondea a 290
    assert market_value(77, 3, 0, ["W", "W", "D", "L", "W"]) == 470  # 385 + 50 + 34 = 469
    assert market_value(77, 3, 2, []) == market_value(77, 3, 0, []) + 80
    assert market_value(80, 4, 0, []) > market_value(79, 3, 0, [])
