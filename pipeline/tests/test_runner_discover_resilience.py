from __future__ import annotations

from pipeline.runner import Runner


class _StubFetcher:
    def get(self, url: str) -> str:
        return "<html></html>"


class _BoomScraper:
    """discover() yields one URL, then raises - as if a roster page 4xx'd mid-walk."""

    name = "boom"
    fetcher = _StubFetcher()

    def discover(self):
        yield "http://example/1"
        raise RuntimeError("roster page failed")

    def extract(self, html: str, url: str):
        return None


class _StubPersister:
    def upsert(self, record):
        return "inserted"


def test_discover_failure_aborts_the_source_not_the_run(monkeypatch):
    scraper = _BoomScraper()
    monkeypatch.setattr("pipeline.runner.get_scraper", lambda name: scraper)

    runner = Runner(persister=_StubPersister())
    summary = runner._scrape_source("boom", _StubPersister())  # must not raise

    assert summary.aborted_reason == "discover_failed"
    assert summary.discovered == 1  # the URL yielded before the failure was still processed
