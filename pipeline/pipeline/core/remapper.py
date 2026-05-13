"""Backfill: re-map every doctor's stored specialty strings against the current
taxonomy + aliases, without re-scraping."""

from __future__ import annotations

from dataclasses import dataclass

import psycopg
import structlog

from pipeline.core.non_providers import NonProviderList
from pipeline.core.specialty_matcher import SpecialtyMatcher
from pipeline.core.specialty_writer import maybe_deactivate, write_doctor_specialties

log = structlog.get_logger("pipeline.remapper")


@dataclass(frozen=True)
class RemapStats:
    total: int
    mapped_before: int
    mapped_after: int
    deactivated: int


class RemapRegression(RuntimeError):
    """Raised when a remap would reduce the mapped-doctor count; the transaction
    is rolled back so the prior mappings are preserved."""

    def __init__(self, stats: "RemapStats") -> None:
        super().__init__(f"remap regressed: {stats.mapped_after} < {stats.mapped_before}")
        self.stats = stats


def _count_mapped(cur: psycopg.Cursor) -> int:
    cur.execute(
        "SELECT count(DISTINCT d.id) FROM doctor d "
        "JOIN doctor_specialty ds ON ds.doctor_id = d.id WHERE d.status = 'ACTIVE'"
    )
    return cur.fetchone()[0]


class Remapper:
    def __init__(
        self,
        dsn: str,
        *,
        matcher: SpecialtyMatcher,
        non_providers: NonProviderList | None = None,
    ) -> None:
        self._dsn = dsn
        self._matcher = matcher
        self._non_providers = non_providers

    def remap_all(self) -> RemapStats:
        with psycopg.connect(self._dsn) as conn, conn.cursor() as cur:
            mapped_before = _count_mapped(cur)
            cur.execute("SELECT id, specialty_ka, specialty_en FROM doctor")
            rows = cur.fetchall()
            deactivated = 0
            for doctor_id, specialty_ka, specialty_en in rows:
                cur.execute("DELETE FROM doctor_specialty WHERE doctor_id = %s", (doctor_id,))
                mapped = write_doctor_specialties(cur, doctor_id, specialty_ka, specialty_en, self._matcher)
                if maybe_deactivate(cur, doctor_id, specialty_ka, specialty_en, self._non_providers, mapped):
                    deactivated += 1
            mapped_after = _count_mapped(cur)
            stats = RemapStats(
                total=len(rows), mapped_before=mapped_before,
                mapped_after=mapped_after, deactivated=deactivated,
            )
            if mapped_after < mapped_before:
                log.error("remap_regression", **stats.__dict__)
                raise RemapRegression(stats)
            conn.commit()
        log.info("remap_complete", **stats.__dict__)
        return stats
