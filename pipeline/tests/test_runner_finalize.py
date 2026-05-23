from __future__ import annotations

from pipeline.core.runner import Runner


class _Spy:
    def __init__(self):
        self.calls = 0

    def run(self):
        self.calls += 1


def test_run_source_finalizes_once(monkeypatch):
    spy = _Spy()
    r = Runner(persister=object(), deduplicator=spy)
    monkeypatch.setattr(r, "_ensure_seeded", lambda: None)
    monkeypatch.setattr(r, "_scrape_source", lambda name: name)
    r.run_source("evex")
    assert spy.calls == 1


def test_run_all_finalizes_once(monkeypatch):
    spy = _Spy()
    r = Runner(persister=object(), deduplicator=spy)
    monkeypatch.setattr(r, "_ensure_seeded", lambda: None)
    monkeypatch.setattr(r, "_scrape_source", lambda name: name)
    monkeypatch.setattr("pipeline.core.runner.SCRAPERS", {"a": 1, "b": 1})
    r.run_all()
    assert spy.calls == 1
