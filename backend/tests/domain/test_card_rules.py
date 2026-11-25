from app.domain.card_rules import media, tier


def test_media_starts_neutral_and_grows_only_by_playing():
    assert media(0, 0, 0, None, 0) == 57  # 40 + 5,5 × 3 = 56,5, sube a 57
    assert media(1, 1, 3, None, 0) == 71  # 40 + 16,5 + 0,3 + 10 + 4
    assert media(50, 50, 80, 10.0, 30) == 99  # tope
    assert media(50, 50, 80, 10.0, 2) == 86  # menos de 3 votos: valoración neutral (85,5 sube a 86)
    assert media(0, 0, 0, 6.0, 3) == 58  # 40 + 18


def test_bad_ratings_lower_the_media():
    assert media(20, 10, 5, 3.0, 8) < media(20, 10, 5, 8.0, 8)


def test_tiers_by_confirmed_matches():
    assert (tier(0).name, tier(0).next_name, tier(0).matches_to_next) == ("BRONCE", "PLATA", 10)
    assert (tier(19).name, tier(19).matches_to_next) == ("PLATA", 1)
    assert (tier(24).name, tier(24).next_name, tier(24).matches_to_next) == ("ORO", "ELITE", 6)
    assert (tier(30).name, tier(30).next_name, tier(30).matches_to_next) == ("ELITE", None, 0)
