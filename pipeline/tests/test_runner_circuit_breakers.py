from collections.abc import Iterator

import pytest

from pipeline.core.fetcher import FetchError
from pipeline.core.persister import Persister
from pipeline.core.record import DoctorRecord
from pipeline.core.registry import SCRAPERS, register
from pipeline.core.runner import Runner


pytestmark = pytest.mark.slow


@pytest.fixture(autouse=True)
def _clear_registry():
    saved = dict(SCRAPERS)
    SCRAPERS.clear()
    yield
    SCRAPERS.clear()
    SCRAPERS.update(saved)


class _FailingFetcher:
    def __init__(self, fail_count: int, html: str = "<doctor>") -> None:
        self._fail_count = fail_count
        self._calls = 0
        self._html = html

    def get(self, url: str) -> str:
        self._calls += 1
        if self._calls <= self._fail_count:
            raise FetchError("simulated", status_code=403)
        return self._html


class _OkFetcher:
    def get(self, url: str) -> str:
        return "<doctor>"


class _ScraperWithUrls:
    name = "fake-cb"

    def __init__(self, n: int, fetcher) -> None:
        self._urls = [f"https://example.test/{i}" for i in range(n)]
        self.fetcher = fetcher

    def discover(self) -> Iterator[str]:
        yield from self._urls

    def extract(self, html: str, url: str) -> DoctorRecord | None:
        if html == "skip":
            return None
        return DoctorRecord(source=self.name, source_url=url, full_name_ka="დოქტორი")


def test_circuit_breaker_aborts_after_50pct_fetch_failures(clean_doctor_table):
    register(_ScraperWithUrls(20, _FailingFetcher(fail_count=11)))  # 11/20 ≥ 50%
    runner = Runner(persister=Persister(clean_doctor_table))
    summary = runner.run_source("fake-cb")
    assert summary.aborted_reason == "fetch_failure_rate_exceeded"
    assert summary.discovered < 20


def test_circuit_breaker_does_not_trip_below_threshold(clean_doctor_table):
    register(_ScraperWithUrls(20, _FailingFetcher(fail_count=3)))  # 3/20 = 15%
    runner = Runner(persister=Persister(clean_doctor_table))
    summary = runner.run_source("fake-cb")
    assert summary.aborted_reason is None
    assert summary.discovered == 20


def test_circuit_breaker_ignores_first_under_10_attempts(clean_doctor_table):
    register(_ScraperWithUrls(5, _FailingFetcher(fail_count=5)))
    runner = Runner(persister=Persister(clean_doctor_table))
    summary = runner.run_source("fake-cb")
    assert summary.aborted_reason is None
    assert summary.discovered == 5
    assert summary.errors == 5


class _ScraperWithSkips:
    name = "fake-skip"

    def __init__(self, n: int, skip_count: int) -> None:
        self._urls = [f"https://example.test/{i}" for i in range(n)]
        self._skip_count = skip_count
        self._n = n
        self.fetcher = _OkFetcher()

    def discover(self) -> Iterator[str]:
        yield from self._urls

    def extract(self, html: str, url: str) -> DoctorRecord | None:
        idx = int(url.rsplit("/", 1)[-1])
        if idx < self._skip_count:
            return None
        return DoctorRecord(source=self.name, source_url=url, full_name_ka="დოქტორი")


def test_circuit_breaker_aborts_after_20pct_extract_failures(clean_doctor_table):
    register(_ScraperWithSkips(n=20, skip_count=5))  # 5/20 = 25%
    runner = Runner(persister=Persister(clean_doctor_table))
    summary = runner.run_source("fake-skip")
    assert summary.aborted_reason == "extract_skip_rate_exceeded"
    assert summary.discovered < 20
