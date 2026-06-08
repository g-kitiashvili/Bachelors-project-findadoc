"""Runner — orchestrates one scrape cycle per source.

Each scraper carries its own `fetcher` attribute (an HttpxFetcher); the Runner
reads `scraper.fetcher.get(url)` per profile URL.
"""

from __future__ import annotations

import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import structlog

from pipeline.infra.fetcher import FetchError
from pipeline.services.persister import Persister
from pipeline.scrapers.registry import SCRAPERS, get_scraper
from pipeline.domain.translit import normalize

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator, Sequence

    from pipeline.services.pass_base import Pass
    from pipeline.services.seeder_base import Seeder


log = structlog.get_logger("pipeline.runner")


@dataclass
class SourceSummary:
    source: str
    discovered: int = 0
    extracted: int = 0
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0
    aborted_reason: str | None = None
    elapsed_s: float = 0.0
    cycle_id: str = field(default_factory=lambda: uuid.uuid4().hex)


class Runner:
    def __init__(
        self,
        *,
        persister: Persister,
        seeders: "Sequence[Seeder]" = (),
        post_passes: "Sequence[Pass]" = (),
        persister_factory: "Callable[[], Persister] | None" = None,
        scrape_workers: int = 1,
    ) -> None:
        self._persister = persister
        self._seeders = seeders
        self._post_passes = post_passes
        # A fresh persister per worker avoids races on the shared matcher/location caches.
        # scrape_workers: 0 = one thread per source, 1 = sequential, N = cap at N.
        self._persister_factory = persister_factory
        self._scrape_workers = scrape_workers
        self._seeded = False

    def _ensure_seeded(self) -> None:
        # Seeders run once, in the order supplied (conditions resolve onto specialties,
        # so specialties must seed before conditions).
        if self._seeded:
            return
        for seeder in self._seeders:
            seeder.seed()
        self._seeded = True

    def _scrape_source(self, name: str, persister: Persister) -> SourceSummary:
        scraper = get_scraper(name)
        summary = SourceSummary(source=name)
        bound = log.bind(cycle_id=summary.cycle_id, source=name)
        t0 = time.monotonic()
        bound.info("source_started")

        FETCH_FAIL_THRESHOLD = 0.5
        EXTRACT_SKIP_THRESHOLD = 0.2
        MIN_ATTEMPTS_FOR_BREAKER = 10

        def discovered_urls() -> Iterator[str]:
            # A failure inside discover() (e.g. a roster page 4xx) aborts THIS source,
            # not the whole run; URLs already yielded before the failure are kept.
            try:
                yield from scraper.discover()
            except Exception as e:  # noqa: BLE001
                summary.aborted_reason = "discover_failed"
                bound.error("discover_failed", error=str(e))

        for url in discovered_urls():
            summary.discovered += 1
            url_log = bound.bind(url=url)

            try:
                html = scraper.fetcher.get(url)
            except FetchError as e:
                summary.errors += 1
                url_log.warning("fetch_failed", status=e.status_code, error=str(e))
                if (
                    summary.discovered >= MIN_ATTEMPTS_FOR_BREAKER
                    and summary.errors / summary.discovered >= FETCH_FAIL_THRESHOLD
                ):
                    summary.aborted_reason = "fetch_failure_rate_exceeded"
                    bound.error("circuit_breaker_tripped", reason=summary.aborted_reason)
                    break
                continue

            try:
                record = scraper.extract(html, url)
            except Exception as e:  # noqa: BLE001
                summary.skipped += 1
                url_log.warning("extract_raised", error=str(e))
                if (
                    summary.discovered >= MIN_ATTEMPTS_FOR_BREAKER
                    and summary.skipped / summary.discovered >= EXTRACT_SKIP_THRESHOLD
                ):
                    summary.aborted_reason = "extract_skip_rate_exceeded"
                    bound.error("circuit_breaker_tripped", reason=summary.aborted_reason)
                    break
                continue

            if record is None:
                summary.skipped += 1
                url_log.info("extract_skipped", reason="returned_none")

            if (
                summary.discovered >= MIN_ATTEMPTS_FOR_BREAKER
                and summary.skipped / summary.discovered >= EXTRACT_SKIP_THRESHOLD
            ):
                summary.aborted_reason = "extract_skip_rate_exceeded"
                bound.error("circuit_breaker_tripped", reason=summary.aborted_reason)
                break

            if record is None:
                continue

            summary.extracted += 1
            record = normalize(record)

            try:
                action = persister.upsert(record)
            except Exception as e:  # noqa: BLE001
                summary.errors += 1
                url_log.error("upsert_failed", error=str(e))
                continue

            if action == "inserted":
                summary.inserted += 1
            else:
                summary.updated += 1
            url_log.info("upserted", action=action)

        summary.elapsed_s = round(time.monotonic() - t0, 2)
        bound.info(
            "source_summary",
            discovered=summary.discovered,
            extracted=summary.extracted,
            inserted=summary.inserted,
            updated=summary.updated,
            skipped=summary.skipped,
            errors=summary.errors,
            elapsed_s=summary.elapsed_s,
            aborted_reason=summary.aborted_reason,
        )
        return summary

    def run_source(self, name: str) -> SourceSummary:
        self._ensure_seeded()
        summary = self._scrape_source(name, self._persister)
        self._finalize()
        return summary

    def run_all(self) -> dict[str, SourceSummary]:
        self._ensure_seeded()
        names = list(SCRAPERS)
        # 0 (default) = one thread per source; otherwise cap at the configured count.
        workers = len(names) if self._scrape_workers <= 0 else self._scrape_workers
        if workers > 1 and len(names) > 1 and self._persister_factory is not None:
            summaries = self._scrape_concurrently(names, workers)
        else:
            summaries = {name: self._scrape_source(name, self._persister) for name in names}
        self._finalize()
        return summaries

    def _scrape_concurrently(self, names: list[str], workers: int) -> dict[str, SourceSummary]:
        # One source per worker, each with its own persister (fresh matcher/location
        # caches), so the shared mutable state that the sequential path relies on can't race.
        factory = self._persister_factory
        assert factory is not None
        summaries: dict[str, SourceSummary] = {}
        with ThreadPoolExecutor(max_workers=min(workers, len(names))) as pool:
            futures = {pool.submit(self._scrape_source, name, factory()): name for name in names}
            for future in as_completed(futures):
                summaries[futures[future]] = future.result()
        return summaries

    def _finalize(self) -> None:
        # Post-scrape passes run in the order supplied (dependency order: dedup first,
        # since brands + prominence read its merge clusters; then geocode, brands, prominence).
        for post_pass in self._post_passes:
            post_pass.run()
