"""Idempotent medical-condition seeder: upserts medical_condition by slug and
rebuilds each condition's condition_specialty rows from the curated specialty
slug list. Run after seed-specialties (needs specialty ids)."""

from __future__ import annotations

from pathlib import Path

import psycopg
import structlog

from pipeline.core.taxonomy import load_conditions

log = structlog.get_logger("pipeline.medical_condition_seeder")

_UPSERT = """
INSERT INTO medical_condition (slug, name_ka, name_en, description_ka, description_en, sort_order)
VALUES (%(slug)s, %(name_ka)s, %(name_en)s, %(description_ka)s, %(description_en)s, %(sort_order)s)
ON CONFLICT (slug) DO UPDATE SET
    name_ka = EXCLUDED.name_ka, name_en = EXCLUDED.name_en,
    description_ka = EXCLUDED.description_ka, description_en = EXCLUDED.description_en,
    sort_order = EXCLUDED.sort_order
RETURNING id
"""


class MedicalConditionSeeder:
    def __init__(self, *, dsn: str, yaml_path: Path | str) -> None:
        self._dsn = dsn
        self._yaml_path = Path(yaml_path)

    def seed(self) -> int:
        rows = load_conditions(self._yaml_path)
        with psycopg.connect(self._dsn) as conn, conn.cursor() as cur:
            cur.execute("SELECT slug, id FROM specialty")
            spec_id = {s: i for s, i in cur.fetchall()}
            for row in rows:
                cur.execute(_UPSERT, {
                    "slug": row["slug"],
                    "name_ka": row["name_ka"],
                    "name_en": row["name_en"],
                    "description_ka": row.get("description_ka"),
                    "description_en": row.get("description_en"),
                    "sort_order": row.get("sort_order", 1000),
                })
                cond_id = cur.fetchone()[0]
                cur.execute("DELETE FROM condition_specialty WHERE condition_id = %s", (cond_id,))
                for slug in row.get("specialties", []):
                    sid = spec_id.get(slug)
                    if sid is None:
                        log.warning("condition_specialty_unmapped", condition=row["slug"], specialty=slug)
                        continue
                    cur.execute(
                        "INSERT INTO condition_specialty (condition_id, specialty_id) VALUES (%s, %s) "
                        "ON CONFLICT DO NOTHING",
                        (cond_id, sid),
                    )
                cur.execute("DELETE FROM condition_synonym WHERE condition_id = %s", (cond_id,))
                seen: set[tuple[str, str]] = set()
                for lang, key in (("en", "synonyms_en"), ("ka", "synonyms_ka")):
                    for raw in row.get(key, []) or []:
                        term = (raw or "").strip()
                        dedup_key = (lang, term.lower())
                        if not term or dedup_key in seen:
                            continue
                        seen.add(dedup_key)
                        cur.execute(
                            "INSERT INTO condition_synonym (condition_id, term, lang) VALUES (%s, %s, %s)",
                            (cond_id, term, lang),
                        )
            conn.commit()
        log.info("condition_seed_complete", count=len(rows))
        return len(rows)
