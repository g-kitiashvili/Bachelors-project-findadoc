from __future__ import annotations

from pipeline.runner import Runner


class _Spy:
    def __init__(self):
        self.calls = 0

    def run(self):
        self.calls += 1


def test_run_source_finalizes_once(monkeypatch):
    spy = _Spy()
    r = Runner(persister=object(), post_passes=[spy])
    monkeypatch.setattr(r, "_ensure_seeded", lambda: None)
    monkeypatch.setattr(r, "_scrape_source", lambda name, persister=None: name)
    r.run_source("evex")
    assert spy.calls == 1


def test_run_all_finalizes_once(monkeypatch):
    spy = _Spy()
    r = Runner(persister=object(), post_passes=[spy])
    monkeypatch.setattr(r, "_ensure_seeded", lambda: None)
    monkeypatch.setattr(r, "_scrape_source", lambda name, persister=None: name)
    monkeypatch.setattr("pipeline.runner.SCRAPERS", {"a": 1, "b": 1})
    r.run_all()
    assert spy.calls == 1


def test_run_all_parallel_uses_a_fresh_persister_per_source(monkeypatch):
    spy = _Spy()
    built: list[object] = []

    def factory():
        p = object()
        built.append(p)
        return p

    seen: list[tuple[str, object]] = []
    r = Runner(persister=object(), post_passes=[spy], persister_factory=factory, scrape_workers=0)
    monkeypatch.setattr(r, "_ensure_seeded", lambda: None)
    monkeypatch.setattr(r, "_scrape_source", lambda name, persister: seen.append((name, persister)) or name)
    monkeypatch.setattr("pipeline.runner.SCRAPERS", {"a": 1, "b": 1, "c": 1})

    summaries = r.run_all()

    assert set(summaries) == {"a", "b", "c"}
    assert spy.calls == 1                      # finalize runs exactly once after all sources
    assert len(built) == 3                     # one persister built per source
    assert len({id(p) for _, p in seen}) == 3  # each source got its own persister instance
