import re
from pathlib import Path

import pytest

from pipeline.scrapers.vipmed import VipmedScraper, _strip_md


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "vipmed"


def _read(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def scraper():
    return VipmedScraper()


def test_extract_returns_doctor_with_clinics(scraper):
    record = scraper.extract(_read("profile_1.html"), "https://vipmed.ge/maia-mchedlidze/")
    assert record is not None
    assert record.source == "vipmed"
    assert record.full_name_ka == "მაია მჭედლიძე"
    assert not re.search(r"\bMD\b\s*$", record.full_name_ka, re.IGNORECASE)
    assert len(record.clinics) >= 1


def test_extract_doctor_with_multiple_clinics(scraper):
    record = scraper.extract(_read("profile_2.html"), "https://vipmed.ge/avtandil-tataradze/")
    assert record is not None
    assert record.full_name_ka == "ავთანდილ თათარაძე"
    assert not re.search(r"\bMD\b\s*$", record.full_name_ka, re.IGNORECASE)
    assert len(record.clinics) > 1
    assert all(str(c.source_url).startswith("https://vipmed.ge/clinic/") for c in record.clinics)


def test_extract_returns_none_for_non_profile(scraper):
    assert scraper.extract(_read("non_profile.html"), "https://vipmed.ge/") is None


def test_strip_md():
    assert _strip_md("Giorgi Tsintsadze MD") == "Giorgi Tsintsadze"
    assert _strip_md("Ana Beridze, M.D.") == "Ana Beridze"
    assert _strip_md("მაია მჭედლიძე MD. PhD.") == "მაია მჭედლიძე"
    assert _strip_md("X PhD.") == "X"
    assert _strip_md("Nino Lomidze") == "Nino Lomidze"
    assert _strip_md("MDoe Surname") == "MDoe Surname"


class _FakeFetcher:
    def __init__(self, pages: dict[str, str]) -> None:
        self._pages = pages

    def get(self, url: str) -> str:
        return self._pages.get(url, _read("list_empty.html"))


def test_discover_yields_and_terminates():
    scraper = VipmedScraper(fetcher=_FakeFetcher({"https://vipmed.ge/doctors/": _read("list.html")}))
    urls = list(scraper.discover())
    assert len(urls) >= 1
    assert "https://vipmed.ge/maia-mchedlidze/" in urls
    assert all(u.startswith("https://vipmed.ge/") for u in urls)
