"""Runner — orchestrates one scrape cycle per source.

Each scraper carries its own `fetcher` attribute (HttpxFetcher or
PlaywrightFetcher chosen by the scraper at construction); the Runner reads
`scraper.fetcher.get(url)` per profile URL.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import structlog

from pipeline.core.fetcher import FetchError
from pipeline.core.persister import Persister
from pipeline.core.registry import SCRAPERS, get_scraper
from pipeline.core.translit import normalize

if TYPE_CHECKING:
    from pipeline.core.specialty_seeder import SpecialtySeeder


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
        specialty_seeder: "SpecialtySeeder | None" = None,
    ) -> None:
        self._persister = persister
        self._specialty_seeder = specialty_seeder
        self._seeded = False

    def _ensure_seeded(self) -> None:
        if self._specialty_seeder is not None and not self._seeded:
            self._specialty_seeder.seed()
            self._seeded = True

    def run_source(self, name: str) -> SourceSummary:
        self._ensure_seeded()
        scraper = get_scraper(name)
        summary = SourceSummary(source=name)
        bound = log.bind(cycle_id=summary.cycle_id, source=name)
        t0 = time.monotonic()
        bound.info("source_started")

        FETCH_FAIL_THRESHOLD = 0.5
        EXTRACT_SKIP_THRESHOLD = 0.2
        MIN_ATTEMPTS_FOR_BREAKER = 10

        for url in scraper.discover():
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
                action = self._persister.upsert(record)
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

    def run_all(self) -> dict[str, SourceSummary]:
        self._ensure_seeded()
        return {name: self.run_source(name) for name in list(SCRAPERS)}
