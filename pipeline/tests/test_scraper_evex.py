from pathlib import Path

import pytest

from pipeline.scrapers.evex import EvexScraper


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "evex"


def _read(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def scraper():
    return EvexScraper()


class _FakeFetcher:
    def __init__(self, body: str) -> None:
        self._body = body

    def get(self, url: str) -> str:
        return self._body


def test_extract_returns_doctor_with_clinics(scraper):
    record = scraper.extract(_read("profile_1.json"), "https://admin.evex.ge/api/doctors/x")
    assert record is not None
    assert record.source == "evex"
    assert record.full_name_ka == "ავთანდილ დგებუაძე"
    assert record.specialty_ka == "ზოგადი ქირურგი, ონკო ქირურგი"
    assert record.city == "თბილისი"
    assert str(record.source_url) == "https://evex.ge/ka/archive/chveni-ekimebi/avtandil-dgebuadze"
    assert str(record.photo_url).startswith("https://admin.evex.ge/storage/doctors/")
    assert len(record.clinics) == 3
    assert all(str(c.source_url).startswith("https://admin.evex.ge/api/clinics/") for c in record.clinics)
    assert record.clinics[0].name_ka == "ევექსის კლინიკა დიდ დიღომში"


def test_extract_handles_single_clinic_without_address(scraper):
    record = scraper.extract(_read("profile_2.json"), "https://admin.evex.ge/api/doctors/y")
    assert record is not None
    assert record.city == "ბათუმი"
    assert len(record.clinics) == 1
    assert record.clinics[0].address is None


def test_extract_returns_none_for_non_profile(scraper):
    assert scraper.extract(_read("non_profile.html"), "https://admin.evex.ge/") is None


def test_discover_yields_detail_urls():
    scraper = EvexScraper(fetcher=_FakeFetcher(_read("list.json")))
    urls = list(scraper.discover())
    assert len(urls) == 12
    assert all(u.startswith("https://admin.evex.ge/api/doctors/") for u in urls)
    assert "https://admin.evex.ge/api/doctors/avtandil-dgebuadze" in urls


def test_extract_populates_english(scraper):
    record = scraper.extract(_read("profile_en.json"), "https://evex.ge/ka/archive/chveni-ekimebi/x")
    assert record is not None
    assert record.full_name_en and not any("ა" <= c <= "ჿ" for c in record.full_name_en)
    assert record.specialty_en
    assert record.clinics and record.clinics[0].name_en
