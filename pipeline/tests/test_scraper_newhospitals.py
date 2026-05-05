from pathlib import Path

import pytest

from pipeline.scrapers.newhospitals import NewhospitalsScraper


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "newhospitals"


@pytest.fixture(scope="module")
def scraper():
    return NewhospitalsScraper()


def _read(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_extract_returns_record_for_profile(scraper):
    html = _read("profile_1.html")
    record = scraper.extract(html, "https://newhospitals.ge/ka/doctor/aleko-turiashvili_ka")
    assert record is not None
    assert record.source == "newhospitals"
    assert record.full_name_ka
    assert str(record.source_url) == "https://newhospitals.ge/ka/doctor/aleko-turiashvili_ka"


def test_extract_returns_none_for_non_profile(scraper):
    html = _read("non_profile.html")
    record = scraper.extract(html, "https://newhospitals.ge/")
    assert record is None


def test_extract_includes_brand_clinic(scraper):
    record = scraper.extract(
        _read("profile_1.html"), "https://newhospitals.ge/ka/doctor/aleko-turiashvili_ka"
    )
    assert record is not None
    assert len(record.clinics) == 1
    assert record.clinics[0].name_ka == "ნიუ ჰოსპიტალსი"


def test_extract_populates_photo_when_present(scraper):
    photos = []
    for n in (1, 2, 3):
        record = scraper.extract(_read(f"profile_{n}.html"), f"https://newhospitals.ge/ka/doctor/{n}")
        if record is not None:
            photos.append(record.photo_url)
    assert any(p is not None for p in photos), "expected at least one fixture to have a photo"


def test_extract_populates_bio_ka_when_present(scraper):
    bios = []
    for n in (1, 2, 3):
        record = scraper.extract(_read(f"profile_{n}.html"), f"https://newhospitals.ge/ka/doctor/{n}")
        if record is not None:
            bios.append(record.bio_ka)
    assert any(b for b in bios), "expected at least one fixture to have a Georgian bio"


class _FakeFetcher:
    def __init__(self, html_by_url: dict[str, str]) -> None:
        self._html_by_url = html_by_url

    def get(self, url: str) -> str:
        return self._html_by_url[url]


def test_discover_yields_profile_urls_from_index():
    index_html = _read("index.html")
    scraper = NewhospitalsScraper(
        fetcher=_FakeFetcher({NewhospitalsScraper._INDEX_URL: index_html})
    )
    urls = list(scraper.discover())
    assert len(urls) >= 3
    assert all(u.startswith("https://newhospitals.ge") for u in urls)


def test_extract_populates_specialty_ka(scraper):
    # At least one profile fixture must have a non-empty specialty_ka.
    specialties = []
    for n in (1, 2, 3):
        record = scraper.extract(_read(f"profile_{n}.html"), f"https://newhospitals.ge/ka/doctor/{n}")
        if record is not None and record.specialty_ka:
            specialties.append(record.specialty_ka)
    assert specialties, "expected at least one fixture to produce a specialty_ka"
    # Sanity: specialty should be short (a few words), not the full bio
    assert all(len(s) < 100 for s in specialties), f"specialty too long: {specialties}"
