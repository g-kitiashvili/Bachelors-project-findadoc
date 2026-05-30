"""Specialty mapping — tokenize scraped specialty strings and match against the
canonical taxonomy. A curated alias index (exact match) is tried first; tokens
that miss it fall back to pg_trgm `similarity`."""

from __future__ import annotations

import re
from dataclasses import dataclass

import psycopg
import structlog

from pipeline.core.taxonomy import normalize_alias

log = structlog.get_logger("pipeline.specialty_matcher")


_DELIMITER_RE = re.compile(r",|;|/|–|—|-| და | and ", flags=re.UNICODE)

DEFAULT_THRESHOLD = 0.45

_PEDIATRIC_MARKERS = ("პედიატ", "ბავშვთა", "ნეონ", "pediatr", "paediatr", "neonat", "child")

# Family / general medicine treats all ages. "ოჯახ" matches ოჯახის ექიმი / საოჯახო მედიცინა.
_FAMILY_MEDICINE_MARKERS = ("ოჯახ", "family")

# Job-title fragments stripped before tokenizing so an embedded specialty surfaces
# (e.g. "არითმოლოგიის ცენტრის ხელმძღვანელი" -> "არითმოლოგიის").
_ADMIN_PHRASE_RE = re.compile(
    r"\s*(ცენტრის ხელმძღვანელი"
    r"|სამსახურის (უფროსი|ხელმძღვანელი)"
    r"|განყოფილების ხელმძღვანელი"
    r"|მიმართულების ხელმძღვანელი)",
    flags=re.UNICODE,
)

# Academic-degree / honorific tokens that carry no specialty signal.
_DEGREE_TOKENS = frozenset({
    "md", "phd", "m.d", "ph.d", "msc", "dsc", "დოქტორი", "პროფესორი",
    "მედიცინის აკადემიური დოქტორი", "მედიცინის მეცნიერებათა დოქტორი",
})


def tokenize(raw: str | None) -> list[str]:
    if raw is None:
        return []
    cleaned = _ADMIN_PHRASE_RE.sub("", raw)
    parts = _DELIMITER_RE.split(cleaned)
    tokens = [p.strip().lower() for p in parts if p and p.strip()]
    return [t for t in tokens if t not in _DEGREE_TOKENS]


def _is_pediatric(token: str) -> bool:
    return any(marker in token for marker in _PEDIATRIC_MARKERS)


def _is_family_medicine(token: str) -> bool:
    return any(marker in token for marker in _FAMILY_MEDICINE_MARKERS)


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
    if any(_is_family_medicine(t) for t in tokens):
        return (True, True)
    treats_children = any(_is_pediatric(t) for t in tokens)
    treats_adults = any(not _is_pediatric(t) for t in tokens)
    return (treats_children, treats_adults)


@dataclass(frozen=True)
class MatchResult:
    id: int
    slug: str
    score: float


class SpecialtyMatcher:
    def __init__(
        self,
        *,
        dsn: str,
        threshold: float = DEFAULT_THRESHOLD,
        aliases: dict[str, str] | None = None,
    ) -> None:
        self._dsn = dsn
        self._threshold = threshold
        self._aliases = aliases or {}
        self._slug_to_id: dict[str, int] | None = None  # lazily loaded

    def _resolve_alias(self, token: str | None) -> MatchResult | None:
        if not token:
            return None
        slug = self._aliases.get(normalize_alias(token))
        if slug is None:
            return None
        if self._slug_to_id is None:
            with psycopg.connect(self._dsn) as conn, conn.cursor() as cur:
                cur.execute("SELECT slug, id FROM specialty")
                self._slug_to_id = {s: i for s, i in cur.fetchall()}
        specialty_id = self._slug_to_id.get(slug)
        if specialty_id is None:
            log.warning("alias_slug_missing", token=token, slug=slug)
            return None
        return MatchResult(id=specialty_id, slug=slug, score=1.0)

    def match_whole(self, *, raw_ka: str | None, raw_en: str | None) -> MatchResult | None:
        """Exact-alias match on the full raw string, before the tokenizer splits a
        compound (e.g. "ყბა-სახის ქირურგი" → maxillofacial surgery, not surgery)."""
        for token in (raw_ka, raw_en):
            hit = self._resolve_alias(token)
            if hit is not None:
                return hit
        return None

    def match(self, *, token_ka: str | None, token_en: str | None) -> MatchResult | None:
        if not token_ka and not token_en:
            return None
        for token in (token_ka, token_en):
            hit = self._resolve_alias(token)
            if hit is not None:
                return hit
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
