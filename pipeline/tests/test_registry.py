import pytest

from pipeline.scrapers.registry import SCRAPERS, get_scraper


def test_registry_starts_empty_or_documented():
    assert isinstance(SCRAPERS, dict)


def test_get_scraper_raises_on_unknown_name():
    with pytest.raises(KeyError):
        get_scraper("nonexistent-source")
