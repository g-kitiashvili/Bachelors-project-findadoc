"""Specialty taxonomy loader — shared by the seeder and the matcher.

`specialties.yaml` is the single source of truth. This module loads it and
builds the normalized `alias -> slug` index the matcher uses as an exact-match
fast path before pg_trgm fuzzy matching. Alias keys are the verbatim surface
forms from the corpus (Georgian is inflected, so genitive forms like
`არითმოლოგიის` are listed explicitly alongside nominatives)."""

from __future__ import annotations

from pathlib import Path

import yaml


def normalize_alias(text: str) -> str:
    """Symmetric normalization for alias keys and incoming tokens:
    lowercase + collapse internal whitespace."""
    return " ".join(text.split()).lower()


def load_specialties(yaml_path: Path | str) -> list[dict]:
    rows = yaml.safe_load(Path(yaml_path).read_text(encoding="utf-8")) or []
    if not isinstance(rows, list):
        raise ValueError(f"{yaml_path} must contain a YAML list at the top level")
    return rows


def load_conditions(yaml_path: Path | str) -> list[dict]:
    rows = yaml.safe_load(Path(yaml_path).read_text(encoding="utf-8")) or []
    if not isinstance(rows, list):
        raise ValueError(f"{yaml_path} must contain a YAML list at the top level")
    return rows


def load_brands(yaml_path: Path | str) -> list[dict]:
    return load_conditions(yaml_path)


def detect_lang(text: str) -> str:
    """'ka' if the term contains any Georgian letter, else 'en'."""
    return "ka" if any("ა" <= ch <= "ჰ" for ch in text) else "en"


def load_search_keywords(yaml_path: Path | str) -> list[dict]:
    """Lay/body-part keyword rows ({term_en, term_ka, specialty}). Missing file
    is allowed and yields an empty list, so the seeder works without it."""
    path = Path(yaml_path)
    if not path.exists():
        return []
    rows = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if not isinstance(rows, list):
        raise ValueError(f"{yaml_path} must contain a YAML list at the top level")
    return rows


def build_alias_index(rows: list[dict]) -> dict[str, str]:
    """Normalized alias/name -> slug. A key claimed by two different slugs is a
    curation error and raises, so mistakes surface loudly rather than silently
    mislabeling doctors."""
    index: dict[str, str] = {}
    for row in rows:
        slug = row["slug"]
        for key in (row["name_ka"], row["name_en"], *row.get("aliases", [])):
            norm = normalize_alias(key)
            if not norm:
                continue
            existing = index.get(norm)
            if existing is not None and existing != slug:
                raise ValueError(f"alias {norm!r} maps to both {existing!r} and {slug!r}")
            index[norm] = slug
    return index
