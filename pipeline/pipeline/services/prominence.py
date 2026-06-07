"""Compute an explainable per-doctor prominence score (0-100).

A deterministic, documented weighted sum of four signals - the opposite of an
opaque ranking. Written to `doctor.prominence` by the `prominence` CLI pass and
used by the API as the default browse order (and a relevance tie-break).

Run after `dedup` (corroboration reads the merge clusters) and after specialty
mapping (breadth reads `doctor_specialty`).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from urllib.parse import urlsplit

import structlog

from pipeline.services.pass_base import Pass

log = structlog.get_logger("pipeline.prominence")

# Weights sum to 1.0; corroboration dominates (independent multi-source listing is
# the strongest trust/prominence signal).
_W_CORROBORATION = 0.40
_W_COMPLETENESS = 0.25
_W_BREADTH = 0.20
_W_RECENCY = 0.15


def _host(url: str | None) -> str:
    return urlsplit(url or "").netloc.lower().removeprefix("www.")


def prominence_score(
    *,
    sources: int,
    has_photo: bool,
    has_bio: bool,
    specialties: int,
    clinics: int,
    days_since_update: float | None,
) -> float:
    """Weighted sum of four signals, each normalized to [0,1], scaled to 0-100.

    - corroboration: distinct sources beyond the first, capped at 4 (1 src -> 0, 4+ -> 1)
    - completeness:  has photo, has bio
    - breadth:       specialty count (cap 3) weighted over clinic count (cap 2)
    - recency:       linear decay over a year since the last source update
    """
    corroboration = min(max(sources, 1) - 1, 3) / 3
    completeness = (int(has_photo) + int(has_bio)) / 2
    breadth = 0.6 * (min(specialties, 3) / 3) + 0.4 * (min(clinics, 2) / 2)
    recency = 0.0 if days_since_update is None else max(0.0, 1.0 - days_since_update / 365.0)
    score = (
        _W_CORROBORATION * corroboration
        + _W_COMPLETENESS * completeness
        + _W_BREADTH * breadth
        + _W_RECENCY * recency
    )
    return round(100.0 * score, 2)


@dataclass(frozen=True)
class ProminenceStats:
    scored: int


class ProminencePass(Pass):
    def run(self) -> ProminenceStats:
        with self._db.cursor(autocommit=True) as cur:
            # hosts of every row merged into a canonical doctor, grouped by canonical id
            cur.execute(
                "SELECT merged_into_id, last_source_url FROM doctor WHERE merged_into_id IS NOT NULL"
            )
            merged_hosts: dict[int, list[str]] = defaultdict(list)
            for canonical_id, url in cur.fetchall():
                merged_hosts[canonical_id].append(_host(url))

            cur.execute(
                "SELECT d.id, d.photo_url, d.bio_ka, d.bio_en, d.last_source_url, "
                "EXTRACT(EPOCH FROM (now() - d.last_updated_at)) / 86400.0, "
                "(SELECT count(*) FROM doctor_specialty ds WHERE ds.doctor_id = d.id), "
                "(SELECT count(*) FROM doctor_clinic dc WHERE dc.doctor_id = d.id) "
                "FROM doctor d WHERE d.status = 'ACTIVE'"
            )
            updates: list[tuple[float, int]] = []
            for did, photo, bio_ka, bio_en, url, days, n_spec, n_clin in cur.fetchall():
                sources = {_host(url)} | set(merged_hosts.get(did, []))
                score = prominence_score(
                    sources=len(sources),
                    has_photo=photo is not None,
                    has_bio=bool(bio_ka or bio_en),
                    specialties=int(n_spec),
                    clinics=int(n_clin),
                    days_since_update=float(days) if days is not None else None,
                )
                updates.append((score, did))

            cur.executemany("UPDATE doctor SET prominence = %s WHERE id = %s", updates)
            stats = ProminenceStats(scored=len(updates))
            log.info("prominence_complete", **stats.__dict__)
            return stats
