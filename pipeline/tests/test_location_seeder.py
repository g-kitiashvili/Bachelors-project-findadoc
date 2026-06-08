from __future__ import annotations

from pathlib import Path

import psycopg
import pytest

from pipeline.services.location_seeder import LocationSeeder


pytestmark = pytest.mark.slow


@pytest.fixture()
def clean_location_table(postgres_container):
    with psycopg.connect(postgres_container, autocommit=True) as conn:
        conn.execute("TRUNCATE doctor_specialty, doctor, location RESTART IDENTITY CASCADE")
    yield postgres_container


_YAML = """
- slug: tbilisi
  name_ka: თბილისი
  name_en: Tbilisi
  sort_order: 10
- slug: imereti
  name_ka: იმერეთი
  name_en: Imereti
  sort_order: 30
  cities:
    - slug: kutaisi
      name_ka: ქუთაისი
      name_en: Kutaisi
      sort_order: 10
"""


def test_seed_inserts_regions_and_cities_with_parent_links(clean_location_table: str, tmp_path: Path) -> None:
    yaml_file = tmp_path / "locations.yaml"
    yaml_file.write_text(_YAML, encoding="utf-8")

    LocationSeeder(dsn=clean_location_table, yaml_path=yaml_file).seed()

    with psycopg.connect(clean_location_table) as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM location")
        assert cur.fetchone()[0] == 3
        cur.execute(
            """
            SELECT c.slug, p.slug FROM location c
            JOIN location p ON c.parent_id = p.id
            WHERE c.slug = 'kutaisi'
            """
        )
        assert cur.fetchone() == ("kutaisi", "imereti")
        cur.execute("SELECT parent_id FROM location WHERE slug = 'tbilisi'")
        assert cur.fetchone()[0] is None


def test_seed_is_idempotent(clean_location_table: str, tmp_path: Path) -> None:
    yaml_file = tmp_path / "locations.yaml"
    yaml_file.write_text(_YAML, encoding="utf-8")

    seeder = LocationSeeder(dsn=clean_location_table, yaml_path=yaml_file)
    seeder.seed()
    seeder.seed()

    with psycopg.connect(clean_location_table) as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM location")
        assert cur.fetchone()[0] == 3
