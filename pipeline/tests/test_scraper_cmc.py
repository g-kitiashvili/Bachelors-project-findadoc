from pathlib import Path

import pytest

from pipeline.scrapers.cmc import CmcScraper


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "cmc"


def _read(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def scraper():
    return CmcScraper()


class _FakeFetcher:
    def __init__(self, body: str) -> None:
        self._body = body

    def get(self, url: str) -> str:
        return self._body


def test_extract_returns_doctor_with_single_clinic(scraper):
    record = scraper.extract(
        _read("profile_1.html"), "https://cmchospital.ge/ge/doctors/284-levani-makhaldiani"
    )
    assert record is not None
    assert record.source == "cmc"
    assert record.full_name_ka == "ლევან მახალდიანი"
    assert record.specialty_ka
    assert len(record.clinics) == 1
    assert record.clinics[0].name_ka == "კავკასიის მედიცინის ცენტრი"
    assert str(record.photo_url).startswith("https://app.cmchospital.ge/static/media/")


def test_extract_second_profile(scraper):
    record = scraper.extract(
        _read("profile_2.html"), "https://cmchospital.ge/ge/doctors/270-vladimer-tsikarishvili"
    )
    assert record is not None
    assert record.full_name_ka == "ვლადიმერ წიქარიშვილი"
    assert len(record.clinics) == 1


def test_extract_returns_none_for_non_profile(scraper):
    assert scraper.extract(_read("non_profile.html"), "https://cmchospital.ge/ge") is None


def test_discover_yields_profile_urls():
    scraper = CmcScraper(fetcher=_FakeFetcher(_read("list.html")))
    urls = list(scraper.discover())
    assert len(urls) >= 1
    assert all(u.startswith("https://cmchospital.ge/ge/doctors/") for u in urls)
    assert "https://cmchospital.ge/ge/doctors/270-vladimer-tsikarishvili" in urls


def test_index_urls_paginate():
    scraper = CmcScraper(fetcher=_FakeFetcher(_read("list.html")))
    gen = scraper.index_urls()
    first = [next(gen) for _ in range(3)]
    assert first[0] == "https://cmchospital.ge/ge/doctors?page=1"
    assert first[1].endswith("page=2")
    assert all("page=" in u for u in first)


class _PagedFetcher:
    def __init__(self, first_body: str, empty_body: str) -> None:
        self._first = first_body
        self._empty = empty_body

    def get(self, url: str) -> str:
        return self._first if url.endswith("page=1") else self._empty


def test_discover_stops_on_empty_page():
    scraper = CmcScraper(
        fetcher=_PagedFetcher(_read("list.html"), "<html><body>no doctors here</body></html>")
    )
    urls = list(scraper.discover())
    assert len(urls) >= 1
    assert all(u.startswith("https://cmchospital.ge/ge/doctors/") for u in urls)


class _EnFetcher:
    def __init__(self, pages: dict) -> None:
        self._pages = pages

    def get(self, url: str) -> str:
        return self._pages[url]


def test_extract_sets_english_name_and_clinic():
    ka_url = "https://cmchospital.ge/ge/doctors/284-levani-makhaldiani"
    en_url = ka_url.replace("/ge/", "/en/", 1)
    scraper = CmcScraper(fetcher=_EnFetcher({en_url: _read("profile_1_en.html")}))
    record = scraper.extract(_read("profile_1.html"), ka_url)
    assert record.full_name_en == "Levan Makhaldiani"
    assert record.clinics[0].name_en == "Caucasus Medical Centre"
