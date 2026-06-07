"""Per-doctor specialty writing + non-provider deactivation, shared by the live
persister and the remap backfill."""

from __future__ import annotations

import psycopg
import structlog

from pipeline.domain.non_providers import NonProviderList
from pipeline.services.specialty_matcher import SpecialtyMatcher, tokenize

log = structlog.get_logger("pipeline.specialty_writer")

_UPSERT_DOCTOR_SPECIALTY_SQL = """
INSERT INTO doctor_specialty (doctor_id, specialty_id, is_primary)
VALUES (%(doctor_id)s, %(specialty_id)s, %(is_primary)s)
ON CONFLICT (doctor_id, specialty_id) DO UPDATE
SET is_primary = doctor_specialty.is_primary OR EXCLUDED.is_primary
"""


def write_doctor_specialties(
    cur: psycopg.Cursor,
    doctor_id: int,
    specialty_ka: str | None,
    specialty_en: str | None,
    matcher: SpecialtyMatcher,
) -> int:
    """Tokenize the raw specialty strings, match each token, and upsert
    doctor_specialty rows (first resolved token is primary). Returns the number
    of distinct specialties written."""
    # A full string that is itself a canonical (sub-)specialty alias maps as one
    # specialty, before the tokenizer would split a hyphen compound into its parts.
    whole = matcher.match_whole(raw_ka=specialty_ka, raw_en=specialty_en)
    if whole is not None:
        cur.execute(
            _UPSERT_DOCTOR_SPECIALTY_SQL,
            {"doctor_id": doctor_id, "specialty_id": whole.id, "is_primary": True},
        )
        return 1

    ka_tokens = tokenize(specialty_ka)
    en_tokens = tokenize(specialty_en)
    max_len = max(len(ka_tokens), len(en_tokens))
    if max_len == 0:
        return 0
    seen: set[int] = set()
    for i in range(max_len):
        tk = ka_tokens[i] if i < len(ka_tokens) else None
        te = en_tokens[i] if i < len(en_tokens) else None
        result = matcher.match(token_ka=tk, token_en=te)
        if result is None:
            log.warning(
                "specialty_unmapped",
                doctor_id=doctor_id,
                raw_string_ka=specialty_ka,
                raw_string_en=specialty_en,
                token_ka=tk,
                token_en=te,
            )
            continue
        if result.id in seen:
            continue
        is_primary = len(seen) == 0
        seen.add(result.id)
        cur.execute(
            _UPSERT_DOCTOR_SPECIALTY_SQL,
            {"doctor_id": doctor_id, "specialty_id": result.id, "is_primary": is_primary},
        )
    return len(seen)


def maybe_deactivate(
    cur: psycopg.Cursor,
    doctor_id: int,
    specialty_ka: str | None,
    specialty_en: str | None,
    non_providers: NonProviderList | None,
    mapped_count: int,
) -> bool:
    """Set the doctor's status from the mapping outcome. A doctor that maps to a
    real specialty is (re)activated; one that maps to nothing AND matches a known
    non-provider role is deactivated. Returns True if it was deactivated."""
    if mapped_count > 0:
        cur.execute(
            "UPDATE doctor SET status = 'ACTIVE' WHERE id = %s AND status = 'INACTIVE'",
            (doctor_id,),
        )
        return False
    if non_providers is None or not non_providers.matches(specialty_ka, specialty_en):
        return False
    cur.execute("UPDATE doctor SET status = 'INACTIVE' WHERE id = %s", (doctor_id,))
    return True
