from __future__ import annotations

from pathlib import Path

import psycopg
import pytest

from pipeline.core.specialty_seeder import SpecialtySeeder


pytestmark = pytest.mark.slow


@pytest.fixture()
def clean_specialty_table(postgres_container):
    with psycopg.connect(postgres_container, autocommit=True) as conn:
        conn.execute("TRUNCATE doctor_specialty, specialty RESTART IDENTITY")
    yield postgres_container


def test_seeder_upsert_by_slug_is_idempotent(clean_specialty_table: str, tmp_path: Path) -> None:
    yaml_text = """
- slug: cardiology
  name_ka: კარდიოლოგია
  name_en: Cardiology
  sort_order: 10
- slug: neurology
  name_ka: ნევროლოგია
  name_en: Neurology
  sort_order: 70
"""
    yaml_file = tmp_path / "specialties.yaml"
    yaml_file.write_text(yaml_text, encoding="utf-8")

    seeder = SpecialtySeeder(dsn=clean_specialty_table, yaml_path=yaml_file)
    seeder.seed()
    seeder.seed()

    with psycopg.connect(clean_specialty_table) as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM specialty")
        assert cur.fetchone()[0] == 2
        cur.execute("SELECT slug, name_en FROM specialty ORDER BY sort_order ASC")
        assert cur.fetchall() == [("cardiology", "Cardiology"), ("neurology", "Neurology")]


def test_seeder_updates_existing_rows_on_rerun(clean_specialty_table: str, tmp_path: Path) -> None:
    yaml_file = tmp_path / "specialties.yaml"
    yaml_file.write_text(
        "- slug: cardiology\n  name_ka: კარდიოლოგია\n  name_en: Cardiology\n  sort_order: 10\n",
        encoding="utf-8",
    )
    SpecialtySeeder(dsn=clean_specialty_table, yaml_path=yaml_file).seed()

    yaml_file.write_text(
        "- slug: cardiology\n  name_ka: კარდიოლოგია\n  name_en: Cardiology Updated\n  sort_order: 5\n",
        encoding="utf-8",
    )
    SpecialtySeeder(dsn=clean_specialty_table, yaml_path=yaml_file).seed()

    with psycopg.connect(clean_specialty_table) as conn, conn.cursor() as cur:
        cur.execute("SELECT name_en, sort_order FROM specialty WHERE slug = 'cardiology'")
        assert cur.fetchone() == ("Cardiology Updated", 5)
