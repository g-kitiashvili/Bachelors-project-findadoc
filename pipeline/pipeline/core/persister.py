"""Persister — owns ALL doctor-table SQL.

Idempotency: ON CONFLICT (last_source_url) DO UPDATE.
Slug collisions: retry with -2, -3, ..., -99 (then raise).

When a `SpecialtyMatcher` is provided, also writes `doctor_specialty` rows by
tokenizing the scraped specialty strings and matching tokens against the
canonical taxonomy. Unmatched tokens log a `specialty_unmapped` warning.
"""

from __future__ import annotations

from typing import Literal

import psycopg
import structlog
from psycopg.errors import UniqueViolation

from pipeline.core.location_matcher import LocationMatcher
from pipeline.core.non_providers import NonProviderList
from pipeline.core.record import ClinicRef, DoctorRecord
from pipeline.core.specialty_matcher import SpecialtyMatcher, infer_age_groups
from pipeline.core.specialty_writer import maybe_deactivate, write_doctor_specialties
from pipeline.core.translit import clinic_name_to_en, next_slug_candidate, slugify


SOURCE_CITY = {
    "newhospitals": "tbilisi",
    "aversi": "tbilisi",
    "vivomedical": "tbilisi",
}

_UPSERT_DOCTOR_SQL = """
INSERT INTO doctor (
    slug, full_name_ka, full_name_en, family_name_ka, family_name_en, photo_url, bio_ka, bio_en, gender,
    specialty_ka, specialty_en, treats_children, treats_adults, location_id,
    last_source_url, last_updated_at, status
) VALUES (
    %(slug)s, %(full_name_ka)s, %(full_name_en)s, %(family_name_ka)s, %(family_name_en)s, %(photo_url)s, %(bio_ka)s, %(bio_en)s, %(gender)s,
    %(specialty_ka)s, %(specialty_en)s, %(treats_children)s, %(treats_adults)s, %(location_id)s,
    %(source_url)s, NOW(), 'ACTIVE'
)
ON CONFLICT (last_source_url) DO UPDATE SET
    full_name_ka    = EXCLUDED.full_name_ka,
    full_name_en    = EXCLUDED.full_name_en,
    family_name_ka  = EXCLUDED.family_name_ka,
    family_name_en  = EXCLUDED.family_name_en,
    photo_url       = EXCLUDED.photo_url,
    bio_ka          = EXCLUDED.bio_ka,
    bio_en          = EXCLUDED.bio_en,
    gender          = EXCLUDED.gender,
    specialty_ka    = EXCLUDED.specialty_ka,
    specialty_en    = EXCLUDED.specialty_en,
    treats_children = EXCLUDED.treats_children,
    treats_adults   = EXCLUDED.treats_adults,
    location_id     = EXCLUDED.location_id,
    last_updated_at = EXCLUDED.last_updated_at
RETURNING id, (xmax = 0) AS inserted
"""

_UPSERT_CLINIC_SQL = """
INSERT INTO clinic (slug, name_ka, name_en, address, phone, website, last_source_url, last_updated_at, status)
VALUES (%(slug)s, %(name_ka)s, %(name_en)s, %(address)s, %(phone)s, %(website)s, %(source_url)s, NOW(), 'ACTIVE')
ON CONFLICT (last_source_url) DO UPDATE SET
    name_ka = EXCLUDED.name_ka, name_en = EXCLUDED.name_en, address = EXCLUDED.address,
    phone = EXCLUDED.phone, website = EXCLUDED.website, last_updated_at = EXCLUDED.last_updated_at
RETURNING id
"""

_UPSERT_DOCTOR_CLINIC_SQL = """
INSERT INTO doctor_clinic (doctor_id, clinic_id) VALUES (%(doctor_id)s, %(clinic_id)s)
ON CONFLICT (doctor_id, clinic_id) DO NOTHING
"""


log = structlog.get_logger("pipeline.persister")


def _last_token(name: str | None) -> str | None:
    if not name:
        return None
    parts = name.split()
    return parts[-1] if parts else None


class Persister:
    def __init__(
        self,
        dsn: str,
        *,
        specialty_matcher: SpecialtyMatcher | None = None,
        location_matcher: LocationMatcher | None = None,
        non_providers: NonProviderList | None = None,
    ) -> None:
        self._dsn = dsn
        self._matcher = specialty_matcher
        self._location_matcher = location_matcher
        self._non_providers = non_providers
        self._location_cache: dict[str, int | None] = {}

    def upsert(self, record: DoctorRecord) -> Literal["inserted", "updated"]:
        assert record.full_name_en is not None, "Record must be normalized before upsert"
        assert record.slug_base is not None, "Record must be normalized before upsert"

        treats_children, treats_adults = infer_age_groups(
            record.specialty_ka, record.specialty_en
        )
        location_id = self._resolve_location_id(record)
        for attempt in range(1, 100):
            slug = next_slug_candidate(record.slug_base, attempt)
            params = {
                "slug": slug,
                "full_name_ka": record.full_name_ka,
                "full_name_en": record.full_name_en,
                "family_name_ka": _last_token(record.full_name_ka),
                "family_name_en": _last_token(record.full_name_en),
                "photo_url": str(record.photo_url) if record.photo_url else None,
                "bio_ka": record.bio_ka,
                "bio_en": record.bio_en,
                "gender": record.gender,
                "specialty_ka": record.specialty_ka,
                "specialty_en": record.specialty_en,
                "treats_children": treats_children,
                "treats_adults": treats_adults,
                "location_id": location_id,
                "source_url": str(record.source_url),
            }
            try:
                with psycopg.connect(self._dsn, autocommit=True) as conn, conn.cursor() as cur:
                    cur.execute(_UPSERT_DOCTOR_SQL, params)
                    doctor_id, inserted = cur.fetchone()
                    mapped = self._write_specialties(cur, doctor_id, record)
                    maybe_deactivate(
                        cur, doctor_id, record.specialty_ka, record.specialty_en,
                        self._non_providers, mapped,
                    )
                    self._write_clinics(cur, doctor_id, record)
                    return "inserted" if inserted else "updated"
            except UniqueViolation as e:
                if "doctor_slug_key" not in str(e):
                    raise
                continue
        raise RuntimeError(f"slug collision exhausted for base={record.slug_base!r}")

    def _resolve_location_id(self, record: DoctorRecord) -> int | None:
        if record.city:
            if self._location_matcher is not None:
                return self._location_matcher.match_city(record.city)
            return None
        slug = SOURCE_CITY.get(record.source)
        if slug is None:
            log.warning("location_unmapped", source=record.source)
            return None
        if slug in self._location_cache:
            return self._location_cache[slug]
        with psycopg.connect(self._dsn) as conn, conn.cursor() as cur:
            cur.execute("SELECT id FROM location WHERE slug = %s", (slug,))
            row = cur.fetchone()
        location_id = row[0] if row else None
        if location_id is None:
            log.warning("location_unmapped", source=record.source, slug=slug)
        self._location_cache[slug] = location_id
        return location_id

    def _upsert_clinic(self, cur: psycopg.Cursor, clinic: ClinicRef) -> int:
        name_en = clinic.name_en or clinic_name_to_en(clinic.name_ka)
        slug_base = slugify(name_en) or slugify(clinic.name_ka)
        for attempt in range(1, 100):
            params = {
                "slug": next_slug_candidate(slug_base, attempt),
                "name_ka": clinic.name_ka,
                "name_en": name_en,
                "address": clinic.address,
                "phone": clinic.phone,
                "website": str(clinic.website) if clinic.website else None,
                "source_url": str(clinic.source_url),
            }
            try:
                cur.execute(_UPSERT_CLINIC_SQL, params)
                return cur.fetchone()[0]
            except UniqueViolation as e:
                if "clinic_slug_key" not in str(e):
                    raise
                continue
        raise RuntimeError(f"clinic slug collision exhausted for base={slug_base!r}")

    def _write_clinics(self, cur: psycopg.Cursor, doctor_id: int, record: DoctorRecord) -> None:
        for clinic in record.clinics:
            clinic_id = self._upsert_clinic(cur, clinic)
            cur.execute(_UPSERT_DOCTOR_CLINIC_SQL, {"doctor_id": doctor_id, "clinic_id": clinic_id})

    def _write_specialties(self, cur: psycopg.Cursor, doctor_id: int, record: DoctorRecord) -> int:
        if self._matcher is None:
            return 0
        return write_doctor_specialties(
            cur, doctor_id, record.specialty_ka, record.specialty_en, self._matcher
        )
