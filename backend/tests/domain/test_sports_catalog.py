from pathlib import Path

from app.domain.sports_catalog import SportCatalog

CATALOG_PATH = Path(__file__).resolve().parents[2] / "app" / "config" / "sports.json"


def test_catalog_loads_football_modalities():
    catalog = SportCatalog.load(CATALOG_PATH)
    assert catalog.has_modality("FOOTBALL", "F5")
    assert catalog.has_modality("FOOTBALL", "F11")


def test_catalog_includes_basketball_and_baseball():
    catalog = SportCatalog.load(CATALOG_PATH)
    assert catalog.has_sport("BASKETBALL")
    assert catalog.has_sport("BASEBALL")


def test_catalog_rejects_unknown_sport():
    catalog = SportCatalog.load(CATALOG_PATH)
    assert catalog.has_sport("QUIDDITCH") is False


def test_catalog_rejects_modality_of_other_sport():
    catalog = SportCatalog.load(CATALOG_PATH)
    assert catalog.has_modality("BASKETBALL", "F5") is False


def test_catalog_entries_have_spanish_names():
    catalog = SportCatalog.load(CATALOG_PATH)
    football = next(s for s in catalog.sports if s.code == "FOOTBALL")
    assert football.name == "Fútbol"
