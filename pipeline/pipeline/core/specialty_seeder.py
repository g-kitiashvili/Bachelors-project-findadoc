"""Idempotent specialty taxonomy seeder.

Loads `specialties.yaml` and upserts every row into the `specialty` table by slug.
Also rebuilds each specialty's `specialty_alias` search terms from the YAML
`aliases` plus the curated `search_keywords.yaml` body-part list. Runs once at
the start of every scrape job and as a standalone CLI command.
"""

from __future__ import annotations

from pathlib import Path

import psycopg
import structlog

from pipeline.core.taxonomy import detect_lang, load_search_keywords, load_specialties


_UPSERT_SQL = """
INSERT INTO specialty (slug, name_ka, name_en, description_ka, description_en, sort_order)
VALUES (%(slug)s, %(name_ka)s, %(name_en)s, %(description_ka)s, %(description_en)s, %(sort_order)s)
ON CONFLICT (slug) DO UPDATE SET
    name_ka        = EXCLUDED.name_ka,
    name_en        = EXCLUDED.name_en,
    description_ka = EXCLUDED.description_ka,
    description_en = EXCLUDED.description_en,
    sort_order     = EXCLUDED.sort_order
RETURNING id
"""


log = structlog.get_logger("pipeline.specialty_seeder")


class SpecialtySeeder:
    def __init__(self, *, dsn: str, yaml_path: Path | str, keywords_path: Path | str | None = None) -> None:
        self._dsn = dsn
        self._yaml_path = Path(yaml_path)
        self._keywords_path = Path(keywords_path) if keywords_path is not None else None

    def seed(self) -> int:
        rows = load_specialties(self._yaml_path)
        keywords = load_search_keywords(self._keywords_path) if self._keywords_path else []
        aliases_by_slug: dict[str, list[tuple[str, str]]] = {}
        for row in rows:
            terms = [(detect_lang(a), a.strip()) for a in row.get("aliases", []) if a and a.strip()]
            aliases_by_slug.setdefault(row["slug"], []).extend(terms)
        for kw in keywords:
            slug = kw["specialty"]
            for lang, term in (("en", kw.get("term_en")), ("ka", kw.get("term_ka"))):
                if term and term.strip():
                    aliases_by_slug.setdefault(slug, []).append((lang, term.strip()))

        with psycopg.connect(self._dsn) as conn, conn.cursor() as cur:
            for row in rows:
                cur.execute(_UPSERT_SQL, {
                    "slug": row["slug"],
                    "name_ka": row["name_ka"],
                    "name_en": row["name_en"],
                    "description_ka": row.get("description_ka"),
                    "description_en": row.get("description_en"),
                    "sort_order": row.get("sort_order", 1000),
                })
                spec_id = cur.fetchone()[0]
                cur.execute("DELETE FROM specialty_alias WHERE specialty_id = %s", (spec_id,))
                seen: set[tuple[str, str]] = set()
                for lang, term in aliases_by_slug.get(row["slug"], []):
                    dedup_key = (lang, term.lower())
                    if dedup_key in seen:
                        continue
                    seen.add(dedup_key)
                    cur.execute(
                        "INSERT INTO specialty_alias (specialty_id, term, lang) VALUES (%s, %s, %s)",
                        (spec_id, term, lang),
                    )

            known = {row["slug"] for row in rows}
            for kw in keywords:
                if kw["specialty"] not in known:
                    log.warning("search_keyword_unmapped", specialty=kw["specialty"], term=kw.get("term_en"))
            conn.commit()
        log.info("specialty_seed_complete", count=len(rows))
        return len(rows)
