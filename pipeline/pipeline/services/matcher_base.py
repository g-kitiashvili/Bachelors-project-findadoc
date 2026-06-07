"""Base for DB-backed fuzzy matchers.

Both the specialty and location matchers resolve a scraped string against a
canonical table: an exact alias/name hit first, then a pg_trgm `word_similarity`
fallback above a threshold. This base shares the connection + threshold; each
subclass owns its table-specific query (and its own caching strategy).
"""

from __future__ import annotations

from pipeline.infra.db import Database

DEFAULT_THRESHOLD = 0.45


class TrigramMatcher:
    def __init__(self, *, dsn: str, threshold: float = DEFAULT_THRESHOLD) -> None:
        self._db = Database(dsn)
        self._threshold = threshold
