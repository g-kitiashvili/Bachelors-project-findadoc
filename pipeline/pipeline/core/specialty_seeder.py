"""Idempotent specialty taxonomy seeder.

Loads `specialties.yaml` and upserts every row into the `specialty` table by slug.
Runs once at the start of every scrape job and as a standalone CLI command.
"""

from __future__ import annotations

from pathlib import Path

import psycopg
import structlog
import yaml


_UPSERT_SQL = """
INSERT INTO specialty (slug, name_ka, name_en, description_ka, description_en, sort_order)
VALUES (%(slug)s, %(name_ka)s, %(name_en)s, %(description_ka)s, %(description_en)s, %(sort_order)s)
ON CONFLICT (slug) DO UPDATE SET
    name_ka        = EXCLUDED.name_ka,
    name_en        = EXCLUDED.name_en,
    description_ka = EXCLUDED.description_ka,
    description_en = EXCLUDED.description_en,
    sort_order     = EXCLUDED.sort_order
"""


log = structlog.get_logger("pipeline.specialty_seeder")


class SpecialtySeeder:
    def __init__(self, *, dsn: str, yaml_path: Path | str) -> None:
        self._dsn = dsn
        self._yaml_path = Path(yaml_path)

    def seed(self) -> int:
        rows = yaml.safe_load(self._yaml_path.read_text(encoding="utf-8")) or []
        if not isinstance(rows, list):
            raise ValueError(f"{self._yaml_path} must contain a YAML list at the top level")

        params_list = [
            {
                "slug": row["slug"],
                "name_ka": row["name_ka"],
                "name_en": row["name_en"],
                "description_ka": row.get("description_ka"),
                "description_en": row.get("description_en"),
                "sort_order": row.get("sort_order", 1000),
            }
            for row in rows
        ]
        with psycopg.connect(self._dsn, autocommit=True) as conn, conn.cursor() as cur:
            cur.executemany(_UPSERT_SQL, params_list)
        log.info("specialty_seed_complete", count=len(params_list))
        return len(params_list)
