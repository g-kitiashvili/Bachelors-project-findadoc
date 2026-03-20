from collections.abc import Iterator

import psycopg
import pytest

from pipeline.core.record import DoctorRecord
from pipeline.core.runner import Runner, SourceSummary
from pipeline.core.persister import Persister
from pipeline.core.registry import SCRAPERS, register


pytestmark = pytest.mark.slow


class _FakeFetcher:
    def __init__(self, html_by_url: dict[str, str]) -> None:
        self._html_by_url = html_by_url

    def get(self, url: str) -> str:
        return self._html_by_url[url]


class _FakeScraper:
    name = "fake-happy"

    def __init__(self, urls: list[str], html_by_url: dict[str, str]) -> None:
        self._urls = urls
        self.fetcher = _FakeFetcher(html_by_url)

    def discover(self) -> Iterator[str]:
        yield from self._urls

    def extract(self, html: str, url: str) -> DoctorRecord | None:
        if html == "skip":
            return None
        return DoctorRecord(
            source=self.name,
            source_url=url,
            full_name_ka="გიორგი " + url[-1],
        )


@pytest.fixture(autouse=True)
def _clear_registry():
    saved = dict(SCRAPERS)
    SCRAPERS.clear()
    yield
    SCRAPERS.clear()
    SCRAPERS.update(saved)


def test_run_source_happy_path(clean_doctor_table):
    urls = ["https://example.test/a", "https://example.test/b", "https://example.test/c"]
    html = {u: "<doctor>" for u in urls}
    scraper = _FakeScraper(urls, html)
    register(scraper)
    persister = Persister(clean_doctor_table)
    runner = Runner(persister=persister)

    summary = runner.run_source(scraper.name)
    assert isinstance(summary, SourceSummary)
    assert summary.source == scraper.name
    assert summary.discovered == 3
    assert summary.extracted == 3
    assert summary.inserted == 3
    assert summary.updated == 0
    assert summary.skipped == 0
    assert summary.errors == 0

    with psycopg.connect(clean_doctor_table) as conn, conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM doctor")
        assert cur.fetchone()[0] == 3


def test_run_source_second_run_is_idempotent(clean_doctor_table):
    urls = ["https://example.test/a", "https://example.test/b"]
    html = {u: "<doctor>" for u in urls}
    register(_FakeScraper(urls, html))
    runner = Runner(persister=Persister(clean_doctor_table))

    runner.run_source("fake-happy")
    summary = runner.run_source("fake-happy")
    assert summary.inserted == 0
    assert summary.updated == 2


def test_run_source_skips_when_extract_returns_none(clean_doctor_table):
    urls = ["https://example.test/a", "https://example.test/b"]
    html = {"https://example.test/a": "<doctor>", "https://example.test/b": "skip"}
    register(_FakeScraper(urls, html))
    runner = Runner(persister=Persister(clean_doctor_table))
    summary = runner.run_source("fake-happy")
    assert summary.discovered == 2
    assert summary.extracted == 1
    assert summary.skipped == 1


def test_run_all_iterates_every_registered_source(clean_doctor_table):
    register(_FakeScraper(["https://a.test/1"], {"https://a.test/1": "<doctor>"}))
    s2 = _FakeScraper(["https://b.test/1"], {"https://b.test/1": "<doctor>"})
    s2.name = "fake-second"
    register(s2)
    runner = Runner(persister=Persister(clean_doctor_table))
    results = runner.run_all()
    assert set(results) == {"fake-happy", "fake-second"}
    assert all(s.inserted == 1 for s in results.values())
