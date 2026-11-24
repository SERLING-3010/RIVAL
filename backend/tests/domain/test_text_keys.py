from app.domain.text_keys import search_key


def test_accents_and_case_are_ignored():
    assert search_key("  Bogotá ") == search_key("BOGOTA") == "bogota"


def test_enie_is_normalized_for_search():
    assert search_key("Peñas Blancas") == "penas blancas"
