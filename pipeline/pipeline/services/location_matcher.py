"""Match a scraped city string to a canonical `location` row (region or city).

Exact name match (KA or EN) first, then pg_trgm `word_similarity` so noisy
strings like "თბილისი, საბურთალო" still resolve to the city. Cached per string.
"""

from __future__ import annotations

import structlog

from pipeline.services.matcher_base import DEFAULT_THRESHOLD, TrigramMatcher

log = structlog.get_logger("pipeline.location_matcher")


class LocationMatcher(TrigramMatcher):
    def __init__(self, *, dsn: str, threshold: float = DEFAULT_THRESHOLD) -> None:
        super().__init__(dsn=dsn, threshold=threshold)
        self._cache: dict[str, int | None] = {}

    def match_city(self, city: str | None) -> int | None:
        if not city or not city.strip():
            return None
        key = city.strip().lower()
        if key in self._cache:
            return self._cache[key]

        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT id FROM location
                WHERE lower(name_ka) = %(c)s OR lower(name_en) = %(c)s
                LIMIT 1
                """,
                {"c": key},
            )
            row = cur.fetchone()
            if row is None:
                cur.execute(
                    """
                    SELECT id FROM location
                    WHERE GREATEST(word_similarity(name_ka, %(c)s),
                                   word_similarity(name_en, %(c)s)) >= %(t)s
                    ORDER BY GREATEST(word_similarity(name_ka, %(c)s),
                                      word_similarity(name_en, %(c)s)) DESC,
                             (parent_id IS NULL) DESC
                    LIMIT 1
                    """,
                    {"c": key, "t": self._threshold},
                )
                row = cur.fetchone()

        location_id = row[0] if row else None
        if location_id is None:
            log.warning("location_unmapped", city=city)
        self._cache[key] = location_id
        return location_id
