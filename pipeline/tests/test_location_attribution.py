from __future__ import annotations

import psycopg
import pytest

from pipeline.core.location_seeder import LocationSeeder
from pipeline.core.persister import Persister
from pipeline.core.record import DoctorRecord
from pipeline.core.translit import normalize


pytestmark = pytest.mark.slow


@pytest.fixture()
def seeded_locations(postgres_container, tmp_path):
    with psycopg.connect(postgres_container, autocommit=True) as conn:
        conn.execute("TRUNCATE doctor_specialty, doctor, location RESTART IDENTITY CASCADE")
    yaml_file = tmp_path / "locations.yaml"
    yaml_file.write_text(
        "- slug: tbilisi\n  name_ka: თბილისი\n  name_en: Tbilisi\n  sort_order: 10\n",
        encoding="utf-8",
    )
    LocationSeeder(dsn=postgres_container, yaml_path=yaml_file).seed()
    yield postgres_container


def _record(source: str, url: str) -> DoctorRecord:
    return normalize(
        DoctorRecord(
            source=source,
            source_url=url,
            full_name_ka="თამარ მაისურაძე",
            specialty_ka="კარდიოლოგი",
        )
    )


def test_known_source_attributes_location(seeded_locations: str) -> None:
    persister = Persister(seeded_locations)
    persister.upsert(_record("newhospitals", "https://newhospitals.ge/d/1"))

    with psycopg.connect(seeded_locations) as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT l.slug FROM doctor d JOIN location l ON d.location_id = l.id
            WHERE d.last_source_url = 'https://newhospitals.ge/d/1'
            """
        )
        assert cur.fetchone() == ("tbilisi",)


def test_unknown_source_leaves_location_null(seeded_locations: str) -> None:
    persister = Persister(seeded_locations)
    persister.upsert(_record("mystery", "https://mystery.example/d/1"))

    with psycopg.connect(seeded_locations) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT location_id FROM doctor WHERE last_source_url = 'https://mystery.example/d/1'"
        )
        assert cur.fetchone()[0] is None


def test_per_doctor_city_overrides_source_default(seeded_locations: str) -> None:
    from pipeline.core.location_matcher import LocationMatcher
    with psycopg.connect(seeded_locations, autocommit=True) as conn:
        conn.execute(
            "INSERT INTO location (slug, name_ka, name_en, sort_order) "
            "VALUES ('batumi', 'ბათუმი', 'Batumi', 20) ON CONFLICT (slug) DO NOTHING"
        )
    persister = Persister(seeded_locations, location_matcher=LocationMatcher(dsn=seeded_locations))
    rec = _record("tsamali", "https://tsamali.ge/d/1").model_copy(update={"city": "ბათუმი"})
    persister.upsert(rec)
    with psycopg.connect(seeded_locations) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT l.slug FROM doctor d JOIN location l ON d.location_id=l.id "
            "WHERE d.last_source_url='https://tsamali.ge/d/1'"
        )
        assert cur.fetchone() == ("batumi",)
