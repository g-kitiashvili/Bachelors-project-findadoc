from pathlib import Path

import pytest

from pipeline.scrapers.vivomedical import VivomedicalScraper


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "vivomedical"


@pytest.fixture(scope="module")
def scraper():
    return VivomedicalScraper()


def _read(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_page_has_profile_links(scraper):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(_read("list.html"), "lxml")
    found = [a.get("href") for a in soup.select(scraper.profile_link_selector)]
    assert any("/ge/19/" in (h or "") for h in found)


def test_extract_returns_record(scraper):
    record = scraper.extract(_read("profile_1.html"), "https://vivomedical.ge/ge/19/61/konstantine-kipiani")
    assert record is not None
    assert record.source == "vivomedical"
    assert record.full_name_ka
    assert record.city is None


def test_extract_returns_none_for_non_profile(scraper):
    assert scraper.extract(_read("non_profile.html"), "https://vivomedical.ge/ge/") is None


def test_extract_includes_clinic(scraper):
    record = scraper.extract(_read("profile_1.html"), "https://vivomedical.ge/ge/19/61/x")
    assert record is not None and len(record.clinics) == 1
    assert record.clinics[0].name_ka


def test_extract_populates_specialty_ka(scraper):
    record = scraper.extract(_read("profile_1.html"), "https://vivomedical.ge/ge/19/61/konstantine-kipiani")
    assert record is not None and record.specialty_ka


def test_extract_populates_photo_url(scraper):
    photos = []
    for fname, url in (
        ("profile_1.html", "https://vivomedical.ge/ge/19/61/konstantine-kipiani"),
        ("profile_2.html", "https://vivomedical.ge/ge/19/17/mamuka-gonjilashvili"),
    ):
        record = scraper.extract(_read(fname), url)
        if record is not None:
            photos.append(record.photo_url)
    assert any(p is not None for p in photos)


class _FakeFetcher:
    def __init__(self, default_html: str) -> None:
        self._default_html = default_html

    def get(self, url: str) -> str:
        return self._default_html


def test_discover_yields_profile_urls_from_index():
    scraper = VivomedicalScraper(fetcher=_FakeFetcher(_read("list.html")))
    urls = list(scraper.discover())
    assert len(urls) >= 5
    assert all("vivomedical.ge/ge/19/" in u for u in urls)


def test_index_urls_enumerates_clinics():
    scraper = VivomedicalScraper(fetcher=_FakeFetcher(_read("list.html")))
    urls = list(scraper.index_urls())
    assert urls[0] == VivomedicalScraper._INDEX_URL
    assert any("clinic=" in u for u in urls[1:])


class _EnFetcher:
    def __init__(self, pages: dict[str, str]) -> None:
        self._pages = pages

    def get(self, url: str) -> str:
        return self._pages[url]


def test_extract_sets_english_name_and_clinic():
    ka_url = "https://vivomedical.ge/ge/19/61/konstantine-kipiani"
    en_url = ka_url.replace("/ge/", "/en/", 1)
    scraper = VivomedicalScraper(fetcher=_EnFetcher({en_url: _read("profile_1_en.html")}))
    record = scraper.extract(_read("profile_1.html"), ka_url)
    assert record is not None
    assert record.full_name_en == "Konstantine Kipiani"
    assert record.clinics[0].name_en == "Bokhua Memorial Cardiovascular Center"
    assert not any("ა" <= c <= "ჿ" for c in record.clinics[0].name_en)
