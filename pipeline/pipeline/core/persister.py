"""Persister — owns ALL doctor-table SQL.

Idempotency: ON CONFLICT (last_source_url) DO UPDATE.
Slug collisions: retry with -2, -3, ..., -99 (then raise).
"""

from __future__ import annotations

from typing import Literal

import psycopg
from psycopg.errors import UniqueViolation

from pipeline.core.record import DoctorRecord
from pipeline.core.translit import next_slug_candidate


_UPSERT_SQL = """
INSERT INTO doctor (
    slug, full_name_ka, full_name_en, photo_url, bio_ka, bio_en, gender,
    specialty_ka, specialty_en,
    last_source_url, last_updated_at, status
) VALUES (
    %(slug)s, %(full_name_ka)s, %(full_name_en)s, %(photo_url)s, %(bio_ka)s, %(bio_en)s, %(gender)s,
    %(specialty_ka)s, %(specialty_en)s,
    %(source_url)s, NOW(), 'ACTIVE'
)
ON CONFLICT (last_source_url) DO UPDATE SET
    full_name_ka    = EXCLUDED.full_name_ka,
    full_name_en    = EXCLUDED.full_name_en,
    photo_url       = EXCLUDED.photo_url,
    bio_ka          = EXCLUDED.bio_ka,
    bio_en          = EXCLUDED.bio_en,
    gender          = EXCLUDED.gender,
    specialty_ka    = EXCLUDED.specialty_ka,
    specialty_en    = EXCLUDED.specialty_en,
    last_updated_at = EXCLUDED.last_updated_at
RETURNING (xmax = 0) AS inserted
"""


class Persister:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def upsert(self, record: DoctorRecord) -> Literal["inserted", "updated"]:
        assert record.full_name_en is not None, "Record must be normalized before upsert"
        assert record.slug_base is not None, "Record must be normalized before upsert"

        for attempt in range(1, 100):
            slug = next_slug_candidate(record.slug_base, attempt)
            params = {
                "slug": slug,
                "full_name_ka": record.full_name_ka,
                "full_name_en": record.full_name_en,
                "photo_url": str(record.photo_url) if record.photo_url else None,
                "bio_ka": record.bio_ka,
                "bio_en": record.bio_en,
                "gender": record.gender,
                "specialty_ka": record.specialty_ka,
                "specialty_en": record.specialty_en,
                "source_url": str(record.source_url),
            }
            try:
                with psycopg.connect(self._dsn, autocommit=True) as conn, conn.cursor() as cur:
                    cur.execute(_UPSERT_SQL, params)
                    row = cur.fetchone()
                    return "inserted" if row[0] else "updated"
            except UniqueViolation as e:
                if "doctor_slug_key" not in str(e):
                    raise
                continue
        raise RuntimeError(f"slug collision exhausted for base={record.slug_base!r}")
