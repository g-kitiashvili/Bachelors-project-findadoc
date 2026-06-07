
"""Idempotent region/city taxonomy seeder.

Loads `locations.yaml` and upserts every region and city into the `location`
table by slug. Regions are upserted first (parent_id NULL); cities second,
resolving their parent_id from the region slug. Runs once at the start of
every scrape job and as a standalone CLI command.
"""

from __future__ import annotations

import structlog

from pipeline.domain.taxonomy import load_yaml_list
from pipeline.services.seeder_base import Seeder


_UPSERT_REGION_SQL = """
INSERT INTO location (slug, name_ka, name_en, parent_id, sort_order)
VALUES (%(slug)s, %(name_ka)s, %(name_en)s, NULL, %(sort_order)s)
ON CONFLICT (slug) DO UPDATE SET
    name_ka    = EXCLUDED.name_ka,
    name_en    = EXCLUDED.name_en,
    parent_id  = NULL,
    sort_order = EXCLUDED.sort_order
"""

_UPSERT_CITY_SQL = """
INSERT INTO location (slug, name_ka, name_en, parent_id, sort_order)
VALUES (
    %(slug)s, %(name_ka)s, %(name_en)s,
    (SELECT id FROM location WHERE slug = %(parent_slug)s),
    %(sort_order)s
)
ON CONFLICT (slug) DO UPDATE SET
    name_ka    = EXCLUDED.name_ka,
    name_en    = EXCLUDED.name_en,
    parent_id  = EXCLUDED.parent_id,
    sort_order = EXCLUDED.sort_order
"""


log = structlog.get_logger("pipeline.location_seeder")


class LocationSeeder(Seeder):
    def seed(self) -> int:
        regions = load_yaml_list(self._yaml_path)

        region_params = [
            {
                "slug": r["slug"],
                "name_ka": r["name_ka"],
                "name_en": r["name_en"],
                "sort_order": r.get("sort_order", 1000),
            }
            for r in regions
        ]
        city_params = [
            {
                "slug": c["slug"],
                "name_ka": c["name_ka"],
                "name_en": c["name_en"],
                "sort_order": c.get("sort_order", 1000),
                "parent_slug": r["slug"],
            }
            for r in regions
            for c in r.get("cities", [])
        ]

        with self._db.cursor(autocommit=True) as cur:
            cur.executemany(_UPSERT_REGION_SQL, region_params)
            if city_params:
                cur.executemany(_UPSERT_CITY_SQL, city_params)

        total = len(region_params) + len(city_params)
        log.info("location_seed_complete", regions=len(region_params), cities=len(city_params))
        return total
