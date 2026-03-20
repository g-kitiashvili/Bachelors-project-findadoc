"""Placeholder Mkhedruli → Latin transliteration + slug generation.

Quality is rough by design — Increment 5 replaces this with BGN/PCGN and
backfills existing rows.
"""

from __future__ import annotations

import re

from pipeline.core.record import DoctorRecord

_MKHEDRULI_TO_LATIN: dict[str, str] = {
    "ა": "a",  "ბ": "b",  "გ": "g",  "დ": "d",  "ე": "e",
    "ვ": "v",  "ზ": "z",  "თ": "t",  "ი": "i",  "კ": "k",
    "ლ": "l",  "მ": "m",  "ნ": "n",  "ო": "o",  "პ": "p",
    "ჟ": "zh", "რ": "r",  "ს": "s",  "ტ": "t",  "უ": "u",
    "ფ": "p",  "ქ": "k",  "ღ": "gh", "ყ": "q",  "შ": "sh",
    "ჩ": "ch", "ც": "ts", "ძ": "dz", "წ": "ts", "ჭ": "ch",
    "ხ": "kh", "ჯ": "j",  "ჰ": "h",
}

_NON_SLUG = re.compile(r"[^a-z0-9-]+")
_DASH_RUN = re.compile(r"-+")


def mkhedruli_to_latin(s: str) -> str:
    """Char-by-char Mkhedruli → Latin. Non-Georgian chars pass through unchanged."""
    return "".join(_MKHEDRULI_TO_LATIN.get(ch, ch) for ch in s)


def slugify(name: str) -> str:
    """Lowercase Latin slug from a (possibly Georgian) display name."""
    latin = mkhedruli_to_latin(name).lower()
    no_punct = _NON_SLUG.sub("-", latin)
    collapsed = _DASH_RUN.sub("-", no_punct)
    return collapsed.strip("-")


def next_slug_candidate(base: str, attempt: int) -> str:
    """Return `base` on attempt 1, `base-2` on attempt 2, ..., up to `base-99`."""
    if attempt < 1 or attempt > 99:
        raise ValueError(f"attempt must be in [1, 99], got {attempt}")
    if attempt == 1:
        return base
    return f"{base}-{attempt}"


def normalize(record: DoctorRecord) -> DoctorRecord:
    """Fill `full_name_en` and `slug_base` if missing.

    Transliterated EN is title-cased per word (e.g., 'Giorgi Tsintsadze').
    Slug stays lowercase. Returns a new frozen record. Idempotent.
    """
    updates: dict[str, str] = {}
    if record.full_name_en is None:
        latin = mkhedruli_to_latin(record.full_name_ka).strip()
        updates["full_name_en"] = " ".join(w.capitalize() for w in latin.split())
    if record.slug_base is None:
        updates["slug_base"] = slugify(record.full_name_ka)
    if not updates:
        return record
    return record.model_copy(update=updates)
