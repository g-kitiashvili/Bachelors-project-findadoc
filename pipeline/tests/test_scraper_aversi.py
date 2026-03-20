from pathlib import Path
from urllib.parse import unquote

import pytest

from pipeline.scrapers.aversi import AversiScraper


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "aversi"


def _read(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


class _FakeFetcher:
    """In-memory fetcher: maps URLs to fixture HTML."""

    def __init__(self, html_by_url: dict[str, str]) -> None:
        self._html_by_url = html_by_url
        self.calls: list[str] = []

    def get(self, url: str) -> str:
        self.calls.append(url)
        if url not in self._html_by_url:
            from pipeline.core.fetcher import FetchError
            raise FetchError(f"no fixture for {url}", status_code=404)
        return self._html_by_url[url]


def test_extract_returns_record_for_ka_profile():
    # profile_1.html has no EN counterpart (id=18 — KA-only).
    ka_url = "https://aversiclinic.ge/doctors/1/doctor/18/მაია%20აბესაძე"
    en_url = "https://aversiclinic.ge/en/doctors/1/doctor/18/მაია%20აბესაძე"
    fake = _FakeFetcher({en_url: _read("profile_1.html")})  # EN URL serves the KA page (redirect)
    scraper = AversiScraper(fetcher=fake)
    record = scraper.extract(_read("profile_1.html"), ka_url)
    assert record is not None
    assert record.source == "aversi"
    assert record.full_name_ka  # parsed from KA HTML
    # EN attempted but the response is the KA page (same name) — must NOT populate full_name_en
    assert record.full_name_en is None
    assert unquote(str(record.source_url)) == unquote(ka_url)


def test_extract_populates_en_when_distinct_en_page_exists():
    # profile_2.html (KA: ნაილი აბესაძე) ↔ profile_2_en.html (EN: Naili Abesadze)
    ka_url = "https://aversiclinic.ge/doctors/1/doctor/19/ნაილი%20აბესაძე"
    en_url = "https://aversiclinic.ge/en/doctors/1/doctor/19/ნაილი%20აბესაძე"
    fake = _FakeFetcher({en_url: _read("profile_2_en.html")})
    scraper = AversiScraper(fetcher=fake)
    record = scraper.extract(_read("profile_2.html"), ka_url)
    assert record is not None
    assert record.full_name_ka  # KA from KA HTML
    assert record.full_name_en  # EN from EN HTML
    # Latin script in the EN field
    assert all(c.isascii() or c.isspace() for c in record.full_name_en)


def test_extract_returns_none_for_non_profile():
    record = AversiScraper(fetcher=_FakeFetcher({})).extract(
        _read("non_profile.html"), "https://aversiclinic.ge/"
    )
    assert record is None


def test_extract_handles_en_fetch_failure_gracefully():
    # EN URL not in the fetcher mapping → FetchError raised → must NOT propagate;
    # extract should return a KA-only record.
    ka_url = "https://aversiclinic.ge/doctors/1/doctor/18/მაია%20აბესაძე"
    scraper = AversiScraper(fetcher=_FakeFetcher({}))  # empty: every fetch will fail
    record = scraper.extract(_read("profile_1.html"), ka_url)
    assert record is not None
    assert record.full_name_ka
    assert record.full_name_en is None


def test_extract_populates_photo_from_og_image():
    ka_url = "https://aversiclinic.ge/doctors/1/doctor/18/მაია%20აბესაძე"
    scraper = AversiScraper(fetcher=_FakeFetcher({}))
    record = scraper.extract(_read("profile_1.html"), ka_url)
    assert record is not None
    assert record.photo_url is not None


def test_extract_populates_bio_ka():
    ka_url = "https://aversiclinic.ge/doctors/1/doctor/18/მაია%20აბესაძე"
    scraper = AversiScraper(fetcher=_FakeFetcher({}))
    record = scraper.extract(_read("profile_1.html"), ka_url)
    assert record is not None
    assert record.bio_ka  # CV blocks populate this


def test_extract_does_not_call_fetcher_when_url_already_en():
    # Defensive: if extract is called with an EN URL (shouldn't happen via discover,
    # but be robust), don't try to derive a second EN URL.
    en_url = "https://aversiclinic.ge/en/doctors/1/doctor/27/Maka%20Bendiashvili"
    fake = _FakeFetcher({})
    scraper = AversiScraper(fetcher=fake)
    record = scraper.extract(_read("profile_1_en.html"), en_url)
    # No outbound fetch attempted; full_name_ka populated from the EN page text
    assert fake.calls == []
    assert record is not None


def test_discover_yields_urls_from_first_page_within_max_pages_cap():
    # Default max_pages=2 → fetches /doctors/1 and /doctors/2. Both served from fixture
    # (we reuse index.html for both — that's fine, the dedup logic also catches it).
    fake = _FakeFetcher({
        f"{AversiScraper._BASE}/doctors/1": _read("index.html"),
        f"{AversiScraper._BASE}/doctors/2": _read("index.html"),
    })
    scraper = AversiScraper(fetcher=fake, max_pages=2)
    urls = list(scraper.discover())
    assert len(urls) >= 3
    assert all(u.startswith("https://aversiclinic.ge") for u in urls)
    # /doctors/1 and /doctors/2 both fetched
    assert any("/doctors/1" in c for c in fake.calls)
    assert any("/doctors/2" in c for c in fake.calls)


def test_discover_stops_when_page_has_no_cards():
    # /doctors/1 → cards; /doctors/2 → empty page (no a.doctor-card)
    empty_page = "<html><body><h1>nothing here</h1></body></html>"
    fake = _FakeFetcher({
        f"{AversiScraper._BASE}/doctors/1": _read("index.html"),
        f"{AversiScraper._BASE}/doctors/2": empty_page,
    })
    scraper = AversiScraper(fetcher=fake, max_pages=10)
    urls = list(scraper.discover())
    assert len(urls) >= 3
    # Stopped after page 2 (no cards) — did NOT fetch /doctors/3
    assert all("/doctors/3" not in c for c in fake.calls)


def test_discover_deduplicates_within_run():
    # index.html served for both pages → same hrefs appear twice → dedup keeps each once
    fake = _FakeFetcher({
        f"{AversiScraper._BASE}/doctors/1": _read("index.html"),
        f"{AversiScraper._BASE}/doctors/2": _read("index.html"),
    })
    scraper = AversiScraper(fetcher=fake, max_pages=2)
    urls = list(scraper.discover())
    assert len(urls) == len(set(urls))  # no duplicates


def test_extract_populates_specialty_ka_from_ka_profile():
    ka_url = "https://aversiclinic.ge/doctors/1/doctor/18/მაია%20აბესაძე"
    scraper = AversiScraper(fetcher=_FakeFetcher({}))
    record = scraper.extract(_read("profile_1.html"), ka_url)
    assert record is not None
    assert record.specialty_ka  # subtitle parsed


def test_extract_populates_specialty_en_when_en_page_has_distinct_content():
    ka_url = "https://aversiclinic.ge/doctors/1/doctor/19/ნაილი%20აბესაძე"
    en_url = "https://aversiclinic.ge/en/doctors/1/doctor/19/ნაილი%20აბესაძე"
    fake = _FakeFetcher({en_url: _read("profile_2_en.html")})
    scraper = AversiScraper(fetcher=fake)
    record = scraper.extract(_read("profile_2.html"), ka_url)
    assert record is not None
    assert record.specialty_en  # populated from EN page
    # Latin script
    assert all(c.isascii() or c.isspace() or c == '-' for c in record.specialty_en)
