from pathlib import Path

import pytest

from pipeline.scrapers.joann import JoannScraper


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "joann"


def _read(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def scraper():
    return JoannScraper()


class _FakeFetcher:
    def __init__(self, body: str) -> None:
        self._body = body

    def get(self, url: str) -> str:
        return self._body


def test_extract_returns_doctor_with_single_clinic(scraper):
    record = scraper.extract(
        _read("profile_1.html"), "https://joann.ge/eqimebi/aleqsandre-jeiranashvili"
    )
    assert record is not None
    assert record.source == "joann"
    assert record.full_name_ka == "ალექსანდრე ჯეირანაშვილი"
    assert record.specialty_ka
    assert len(record.clinics) == 1
    assert record.clinics[0].name_ka == "ჯო ენის საუნივერსიტეტო ჰოსპიტალი"
    assert str(record.photo_url).startswith("https://joann.ge/wp-content/uploads/")


def test_extract_second_profile(scraper):
    record = scraper.extract(_read("profile_2.html"), "https://joann.ge/eqimebi/nino-janashia")
    assert record is not None
    assert record.full_name_ka == "ნინო ჯანაშია"
    assert len(record.clinics) == 1


def test_extract_returns_none_for_non_profile(scraper):
    assert scraper.extract(_read("non_profile.html"), "https://joann.ge/") is None


def test_discover_yields_profile_urls():
    scraper = JoannScraper(fetcher=_FakeFetcher(_read("list.html")))
    urls = list(scraper.discover())
    assert len(urls) >= 1
    assert all(u.startswith("https://joann.ge/eqimebi/") for u in urls)
    assert "https://joann.ge/eqimebi/nino-janashia" in urls
    assert "https://joann.ge/eqimebi" not in urls


def test_index_urls_single_page():
    scraper = JoannScraper(fetcher=_FakeFetcher(_read("list.html")))
    urls = list(scraper.index_urls())
    assert urls == ["https://joann.ge/eqimebi/"]


def test_discover_stops_on_empty_page():
    scraper = JoannScraper(
        fetcher=_FakeFetcher("<html><body>no doctors here</body></html>")
    )
    assert list(scraper.discover()) == []


class _EnFetcher:
    def __init__(self, pages: dict) -> None:
        self._pages = pages

    def get(self, url: str) -> str:
        return self._pages[url]


def test_extract_sets_english_name():
    ka_url = "https://joann.ge/eqimebi/nino-janashia"
    en_url = "https://joann.ge/en/doctors/nino-janashia/"
    scraper = JoannScraper(fetcher=_EnFetcher({en_url: _read("profile_2_en.html")}))
    record = scraper.extract(_read("profile_2.html"), ka_url)
    assert record is not None
    assert record.full_name_en == "Nino Janashia"
    assert record.clinics[0].name_en == "Jo Ann University Hospital"


def test_extract_georgian_en_falls_back():
    ka_url = "https://joann.ge/eqimebi/aleqsandre-jeiranashvili"
    en_url = "https://joann.ge/en/doctors/aleqsandre-jeiranashvili/"
    scraper = JoannScraper(fetcher=_EnFetcher({en_url: _read("profile_1_en.html")}))
    record = scraper.extract(_read("profile_1.html"), ka_url)
    assert record is not None
    assert record.full_name_en is None
