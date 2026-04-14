from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from pipeline.scrapers.tsamali import TsamaliScraper


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "tsamali"


@pytest.fixture(scope="module")
def scraper():
    return TsamaliScraper()


def _read(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


class _FakeFetcher:
    def __init__(self, html_by_url: dict[str, str]) -> None:
        self._html_by_url = html_by_url

    def get(self, url: str) -> str:
        return self._html_by_url[url]


def test_extract_populates_name_and_specialty(scraper):
    record = scraper.extract(
        _read("profile_1.html"), "https://tsamali.ge/eqimi/zviad-matoshvili/kardiologi"
    )
    assert record is not None
    assert record.source == "tsamali"
    assert record.full_name_ka == "ზვიად მათოშვილი"
    assert record.specialty_ka == "კარდიოლოგი"
    assert str(record.photo_url).startswith("https://tsamali.ge/uploads/doctors/")


def test_extract_returns_none_for_non_profile(scraper):
    assert scraper.extract(_read("non_profile.html"), "https://tsamali.ge/") is None


def test_extract_reads_city_from_discovery_map():
    scraper = TsamaliScraper()
    url = "https://tsamali.ge/eqimi/gela-xozrevanidze/otorinolaringologi"
    scraper._city_by_url[url] = "ბათუმი"
    record = scraper.extract(_read("profile_2.html"), url)
    assert record is not None
    assert record.city == "ბათუმი"


def test_city_list_page_has_main_cards(scraper):
    soup = BeautifulSoup(_read("city_list.html"), "lxml")
    assert soup.select(scraper.profile_link_selector)


def test_discover_attributes_city_per_profile():
    city_list = _read("list.html")
    batumi_page = _read("city_list.html")
    fetcher = _FakeFetcher(
        {
            TsamaliScraper._CITY_LIST_URL: _city_list_with_single_city(city_list, "5", "ბათუმი"),
            "https://tsamali.ge/doctors/city/5": batumi_page,
            "https://tsamali.ge/doctors/city/5/2": _empty_listing(),
        }
    )
    scraper = TsamaliScraper(fetcher=fetcher)
    urls = list(scraper.discover())
    assert urls
    assert all(u.startswith("https://tsamali.ge/eqimi/") for u in urls)
    assert all(scraper._city_by_url[u] == "ბათუმი" for u in urls)


def _city_list_with_single_city(html: str, city_id: str, name: str) -> str:
    return (
        "<html><body>"
        f'<select id="submiter_mimartuleba"><option value="{city_id}">{name} (215)</option></select>'
        "</body></html>"
    )


def _empty_listing() -> str:
    return "<html><body><div class='doctor_items'></div></body></html>"
