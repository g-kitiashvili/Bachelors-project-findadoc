from collections.abc import Iterator

from pipeline.domain.record import DoctorRecord
from pipeline.scrapers.scraper import Scraper


class _NoopFetcher:
    def get(self, url: str) -> str:
        return ""


class _FakeScraper:
    name = "fake"

    def __init__(self) -> None:
        self.fetcher = _NoopFetcher()

    def discover(self) -> Iterator[str]:
        yield "https://example.test/1"
        yield "https://example.test/2"

    def extract(self, html: str, url: str) -> DoctorRecord | None:
        if "doctor" not in html:
            return None
        return DoctorRecord(source=self.name, source_url=url, full_name_ka="ფეიკი")


def test_fake_implements_scraper_protocol():
    s: Scraper = _FakeScraper()
    assert s.name == "fake"
    assert s.fetcher is not None
    assert list(s.discover()) == ["https://example.test/1", "https://example.test/2"]
    assert s.extract("doctor page", "https://example.test/1") is not None
    assert s.extract("404 page", "https://example.test/1") is None
