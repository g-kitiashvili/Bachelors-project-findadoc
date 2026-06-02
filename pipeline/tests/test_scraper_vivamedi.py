from pathlib import Path

import pytest

from pipeline.scrapers.vivamedi import VivamediScraper


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "vivamedi"


@pytest.fixture(scope="module")
def scraper():
    return VivamediScraper()


def _read(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


class _FakeFetcher:
    def __init__(self, default_html: str) -> None:
        self._default_html = default_html

    def get(self, url: str) -> str:
        return self._default_html


def test_list_page_has_profile_links(scraper):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(_read("list.html"), "lxml")
    found = [a.get("href") for a in soup.select(scraper.profile_link_selector)]
    assert any("doctor_id=" in (h or "") for h in found)


def test_extract_returns_record(scraper):
    record = scraper.extract(_read("profile_1.html"), "http://vivamedi.ge/doctor?doctor_id=20")
    assert record is not None
    assert record.source == "vivamedi"
    assert record.full_name_ka == "დოდო პატარიძე"
    assert record.city is None


def test_extract_returns_none_for_non_profile(scraper):
    assert scraper.extract(_read("non_profile.html"), "http://vivamedi.ge/About-Us") is None


def test_extract_includes_brand_clinic(scraper):
    record = scraper.extract(_read("profile_1.html"), "http://vivamedi.ge/doctor?doctor_id=20")
    assert record is not None and len(record.clinics) == 1
    assert record.clinics[0].name_ka == "სამედიცინო ცენტრი ვივამედი"
    assert record.clinics[0].name_en == "Medical Center Vivamedi"


def test_extract_populates_specialty_ka(scraper):
    record = scraper.extract(_read("profile_1.html"), "http://vivamedi.ge/doctor?doctor_id=20")
    assert record is not None and record.specialty_ka == "ეპიდემიოლოგი"


def test_extract_populates_photo_url_without_spaces(scraper):
    record = scraper.extract(_read("profile_1.html"), "http://vivamedi.ge/doctor?doctor_id=20")
    assert record is not None and record.photo_url is not None
    assert " " not in str(record.photo_url)


def test_extract_populates_bio_without_breadcrumb(scraper):
    record = scraper.extract(_read("profile_1.html"), "http://vivamedi.ge/doctor?doctor_id=20")
    assert record is not None and record.bio_ka
    assert not record.bio_ka.startswith("ექიმები")


def test_second_profile_parses(scraper):
    record = scraper.extract(_read("profile_2.html"), "http://vivamedi.ge/doctor?doctor_id=13")
    assert record is not None and record.full_name_ka


def test_discover_yields_profile_urls_from_index():
    scraper = VivamediScraper(fetcher=_FakeFetcher(_read("list.html")))
    urls = list(scraper.discover())
    assert len(urls) >= 10
    assert all("doctor_id=" in u for u in urls)


def test_index_urls_enumerates_pages():
    scraper = VivamediScraper(fetcher=_FakeFetcher(_read("list.html")))
    urls = list(scraper.index_urls())
    assert urls[0] == VivamediScraper._INDEX_URL
    assert any("page=2" in u for u in urls[1:])
