"""Specialty mapping — tokenize scraped specialty strings and match against the
canonical taxonomy via pg_trgm `similarity`."""

from __future__ import annotations

import re
from dataclasses import dataclass

import psycopg


_DELIMITER_RE = re.compile(r",|;|/|-| და | and ", flags=re.UNICODE)

DEFAULT_THRESHOLD = 0.45

_PEDIATRIC_MARKERS = ("პედიატ", "ბავშვთა", "ნეონ", "pediatr", "paediatr", "neonat", "child")


def tokenize(raw: str | None) -> list[str]:
    if raw is None:
        return []
    parts = _DELIMITER_RE.split(raw)
    return [p.strip().lower() for p in parts if p and p.strip()]


def _is_pediatric(token: str) -> bool:
    return any(marker in token for marker in _PEDIATRIC_MARKERS)


def infer_age_groups(
    specialty_ka: str | None, specialty_en: str | None
) -> tuple[bool, bool]:
    """Infer (treats_children, treats_adults) from scraped specialty strings.

    Sources expose no explicit age-group field, so we derive it from the
    specialty: pediatric and neonatal specialties treat children, any other
    specialty treats adults, and a doctor listed with both gets both flags.
    With no specialty information we fall back to adults only.
    """
    tokens = tokenize(specialty_ka) + tokenize(specialty_en)
    if not tokens:
        return (False, True)
    treats_children = any(_is_pediatric(t) for t in tokens)
    treats_adults = any(not _is_pediatric(t) for t in tokens)
    return (treats_children, treats_adults)


@dataclass(frozen=True)
class MatchResult:
    id: int
    slug: str
    score: float


class SpecialtyMatcher:
    def __init__(self, *, dsn: str, threshold: float = DEFAULT_THRESHOLD) -> None:
        self._dsn = dsn
        self._threshold = threshold

    def match(self, *, token_ka: str | None, token_en: str | None) -> MatchResult | None:
        if not token_ka and not token_en:
            return None
        with psycopg.connect(self._dsn) as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT s.id, s.slug,
                       GREATEST(
                           similarity(COALESCE(%(ka)s, ''), s.name_ka),
                           similarity(COALESCE(%(en)s, ''), s.name_en),
                           word_similarity(s.name_ka, COALESCE(%(ka)s, '')),
                           word_similarity(s.name_en, COALESCE(%(en)s, ''))
                       ) AS score
                FROM specialty s
                WHERE GREATEST(
                          similarity(COALESCE(%(ka)s, ''), s.name_ka),
                          similarity(COALESCE(%(en)s, ''), s.name_en),
                          word_similarity(s.name_ka, COALESCE(%(ka)s, '')),
                          word_similarity(s.name_en, COALESCE(%(en)s, ''))
                      ) >= %(threshold)s
                ORDER BY score DESC, s.sort_order ASC
                LIMIT 1
                """,
                {"ka": token_ka, "en": token_en, "threshold": self._threshold},
            )
            row = cur.fetchone()
            if row is None:
                return None
            return MatchResult(id=row[0], slug=row[1], score=float(row[2]))
