"""Link clinics to curated brands by Georgian name-prefix.

Upserts the brand rows from brands.yaml, then sets clinic.brand_id on every ACTIVE
clinic whose normalized name_ka starts with one of a brand's match_ka prefixes.
Reset-then-assign each run, so re-running converges (idempotent). Run after dedup.
Match prefixes are mutually exclusive by construction (see test_brands_yaml), so no
clinic matches two brands."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import structlog

from pipeline.services.pass_base import Pass
from pipeline.domain.taxonomy import load_brands, normalize_alias

log = structlog.get_logger("pipeline.brand_linker")

_UPSERT_BRAND = """
INSERT INTO clinic_brand (slug, name_ka, name_en, sort_order)
VALUES (%(slug)s, %(name_ka)s, %(name_en)s, %(sort_order)s)
ON CONFLICT (slug) DO UPDATE SET
    name_ka = EXCLUDED.name_ka, name_en = EXCLUDED.name_en, sort_order = EXCLUDED.sort_order
RETURNING id
"""


@dataclass(frozen=True)
class BrandLinkStats:
    brands: int
    linked: int


class BrandLinkingPass(Pass):
    def __init__(self, *, dsn: str, yaml_path: Path | str) -> None:
        super().__init__(dsn)
        self._yaml_path = Path(yaml_path)

    def run(self) -> BrandLinkStats:
        brands = load_brands(self._yaml_path)
        with self._db.cursor() as cur:
            brand_id: dict[str, int] = {}
            for b in brands:
                cur.execute(_UPSERT_BRAND, {
                    "slug": b["slug"], "name_ka": b["name_ka"],
                    "name_en": b["name_en"], "sort_order": b.get("sort_order", 1000),
                })
                brand_id[b["slug"]] = cur.fetchone()[0]

            cur.execute("SELECT id, name_ka FROM clinic WHERE status='ACTIVE'")
            clinics = [(cid, normalize_alias(nka or "")) for cid, nka in cur.fetchall()]
            cur.execute("UPDATE clinic SET brand_id = NULL WHERE brand_id IS NOT NULL")

            linked = 0
            for b in brands:
                prefixes = [normalize_alias(p) for p in b["match_ka"]]
                ids = [cid for cid, nka in clinics if any(nka.startswith(p) for p in prefixes)]
                if ids:
                    cur.execute("UPDATE clinic SET brand_id = %s WHERE id = ANY(%s)", (brand_id[b["slug"]], ids))
                    linked += len(ids)
        stats = BrandLinkStats(len(brands), linked)
        log.info("brand_link_complete", **stats.__dict__)
        return stats
