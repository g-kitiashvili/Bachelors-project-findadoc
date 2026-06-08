"""aversi scraper tests — driven by trimmed dashboard-API JSON fixtures.

No network, no Playwright: a fake fetcher maps API URLs to fixture pages. The fake
mirrors the real server in two ways the scraper relies on: it ignores the `_id`
query param (returns the page regardless), and ka/en pages share ids by position.
"""

from pathlib import Path
from urllib.parse import parse_qs, urlsplit, urlunsplit

import pytest

from pipeline.infra.fetcher import FetchError
from pipeline.scrapers.aversi import AversiScraper


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "aversi"


def _read(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def _strip_id(url: str) -> str:
    """Drop the scraper's synthetic `_id` param — the real API ignores it too."""
    parts = urlsplit(url)
    kept = [
        f"{k}={v}"
        for k, vs in parse_qs(parts.query).items()
        if k != "_id"
        for v in vs
    ]
    return urlunsplit(parts._replace(query="&".join(kept), fragment=""))


class _FakeFetcher:
    """In-memory fetcher: maps (id-stripped) API URLs to fixture JSON."""

    def __init__(self, json_by_url: dict[str, str]) -> None:
        self._json_by_url = json_by_url
        self.calls: list[str] = []

    def get(self, url: str) -> str:
        self.calls.append(url)
        key = _strip_id(url)
        if key not in self._json_by_url:
            raise FetchError(f"no fixture for {url} (key={key})", status_code=404)
        return self._json_by_url[key]


_BASE = "https://dashboard.aversiclinic.ge/api/doctors"


def _single_page_fetcher() -> _FakeFetcher:
    """ka/en page 1 present; page 2 empty (stops pagination)."""
    empty = '{"page_number":2,"max_pages":30,"per_page":16,"data":[]}'
    return _FakeFetcher(
        {
            f"{_BASE}/ka?page=1": _read("page1_ka.json"),
            f"{_BASE}/en?page=1": _read("page1_en.json"),
            f"{_BASE}/ka?page=2": empty,
            f"{_BASE}/en?page=2": empty,
        }
    )


def _two_page_fetcher() -> _FakeFetcher:
    """ka/en pages 1 and 10 present (10 stands in for page 2); page 3 empty."""
    empty = '{"page_number":3,"max_pages":30,"per_page":16,"data":[]}'
    return _FakeFetcher(
        {
            f"{_BASE}/ka?page=1": _read("page1_ka.json"),
            f"{_BASE}/en?page=1": _read("page1_en.json"),
            f"{_BASE}/ka?page=2": _read("page10_ka.json"),
            f"{_BASE}/en?page=2": _read("page10_en.json"),
            f"{_BASE}/ka?page=3": empty,
            f"{_BASE}/en?page=3": empty,
        }
    )


def _record_for(scraper: AversiScraper, fake: _FakeFetcher, doctor_id: int):
    """Run discover→fetch→extract for one doctor id, like the Runner does."""
    target = next(u for u in scraper.discover() if f"_id={doctor_id}" in u)
    html = fake.get(target)
    return scraper.extract(html, target)


# --- discover --------------------------------------------------------------


def test_discover_yields_one_dashboard_url_per_doctor():
    fake = _single_page_fetcher()
    scraper = AversiScraper(fetcher=fake)
    urls = list(scraper.discover())
    assert len(urls) == 3  # ids 18, 19, 99001
    assert all(u.startswith("https://dashboard.aversiclinic.ge/api/doctors") for u in urls)
    assert {18, 19, 99001} == {int(parse_qs(urlsplit(u).query)["_id"][0]) for u in urls}


def test_discover_never_fetches_the_cloudflare_spa():
    fake = _two_page_fetcher()
    scraper = AversiScraper(fetcher=fake)
    list(scraper.discover())
    assert all("dashboard.aversiclinic.ge" in c for c in fake.calls)
    assert not any(c.startswith("https://aversiclinic.ge") for c in fake.calls)


def test_discover_stops_on_empty_page():
    fake = _single_page_fetcher()
    scraper = AversiScraper(fetcher=fake)
    list(scraper.discover())
    assert not any("page=3" in c for c in fake.calls)


def test_discover_deduplicates_ids():
    fake = _single_page_fetcher()
    scraper = AversiScraper(fetcher=fake)
    urls = list(scraper.discover())
    assert len(urls) == len(set(urls))


# --- extract: names & english_or_none -------------------------------------


def test_extract_pairs_ka_and_en_name():
    fake = _single_page_fetcher()
    scraper = AversiScraper(fetcher=fake)
    rec = _record_for(scraper, fake, 18)
    assert rec is not None
    assert rec.source == "aversi"
    # KA name is Georgian script
    assert any("ა" <= c <= "ჰ" for c in rec.full_name_ka)
    # EN name is Latin via english_or_none
    assert rec.full_name_en == "Maia Abesadze"
    assert all(c.isascii() for c in rec.full_name_en)


def test_extract_full_name_en_is_none_when_en_name_is_georgian():
    fake = _two_page_fetcher()
    scraper = AversiScraper(fetcher=fake)
    rec = _record_for(scraper, fake, 1077)  # en name "მაკა ალავიძე" (Georgian)
    assert rec is not None
    assert rec.full_name_ka  # KA present
    assert rec.full_name_en is None
    # but the en specialty/branch titles ARE English for this doctor
    assert rec.specialty_en == "Cardiologist"


# --- extract: clinics ------------------------------------------------------


def test_extract_clinic_has_name_ka_and_name_en():
    fake = _single_page_fetcher()
    scraper = AversiScraper(fetcher=fake)
    rec = _record_for(scraper, fake, 18)
    assert rec is not None
    assert len(rec.clinics) == 1
    clinic = rec.clinics[0]
    assert any("ა" <= c <= "ჰ" for c in clinic.name_ka)  # KA branch title
    assert clinic.name_ka.startswith("ავერსი")  # brand-prefixed
    assert clinic.name_en == "Aversi – Central Branch"
    assert clinic.address
    assert str(clinic.source_url).startswith("https://")


def test_extract_clinics_pair_by_branch_id():
    fake = _two_page_fetcher()
    scraper = AversiScraper(fetcher=fake)
    rec = _record_for(scraper, fake, 1081)  # 3 branches
    assert rec is not None
    assert len(rec.clinics) == 3
    en_names = {c.name_en for c in rec.clinics}
    assert {"Aversi – Central Branch", "Aversi – Isani Branch", "Aversi – Gori №1 Branch"} == en_names
    # every clinic has a distinct stable source_url
    assert len({str(c.source_url) for c in rec.clinics}) == 3


def test_extract_falls_back_to_brand_clinic_when_no_branches():
    fake = _single_page_fetcher()
    scraper = AversiScraper(fetcher=fake)
    rec = _record_for(scraper, fake, 99001)  # branchless
    assert rec is not None
    assert len(rec.clinics) == 1
    assert rec.clinics[0].name_ka == "ავერსის კლინიკა"
    assert rec.clinics[0].name_en == "Aversi Clinic"


# --- extract: specialty, photo, gender, source_url ------------------------


def test_extract_populates_specialty_ka():
    fake = _single_page_fetcher()
    scraper = AversiScraper(fetcher=fake)
    rec = _record_for(scraper, fake, 18)
    assert rec is not None
    assert rec.specialty_ka


def test_extract_specialty_en_is_none_when_georgian():
    fake = _two_page_fetcher()
    scraper = AversiScraper(fetcher=fake)
    rec = _record_for(scraper, fake, 1081)
    assert rec is not None
    assert rec.specialty_en == "Rheumatologist"


def test_extract_populates_photo_absolute_url():
    fake = _single_page_fetcher()
    scraper = AversiScraper(fetcher=fake)
    rec = _record_for(scraper, fake, 18)
    assert rec is not None
    assert str(rec.photo_url) == (
        "https://dashboard.aversiclinic.ge/storage/"
        "doctors/7ulpUX2Tm4MYgQHRjfzHpB5pyhJiy3SsmYgBcdrR.webp"
    )


def test_extract_photo_none_when_absent():
    fake = _single_page_fetcher()
    scraper = AversiScraper(fetcher=fake)
    rec = _record_for(scraper, fake, 99001)
    assert rec is not None
    assert rec.photo_url is None


def test_extract_source_url_is_stable_and_distinct_per_doctor():
    fake = _single_page_fetcher()
    scraper = AversiScraper(fetcher=fake)
    r18 = _record_for(scraper, fake, 18)
    r19 = _record_for(scraper, fake, 19)
    assert str(r18.source_url) != str(r19.source_url)
    assert "18" in str(r18.source_url)


def test_extract_returns_none_for_missing_id_in_page():
    fake = _single_page_fetcher()
    scraper = AversiScraper(fetcher=fake)
    page = _read("page1_ka.json")
    # an _id not present in the page → no match → None (not a crash)
    rec = scraper.extract(page, f"{_BASE}/ka?page=1&_id=999999")
    assert rec is None


def test_extract_returns_none_for_non_json():
    scraper = AversiScraper(fetcher=_single_page_fetcher())
    rec = scraper.extract("<html>not json</html>", f"{_BASE}/ka?page=1&_id=18")
    assert rec is None
