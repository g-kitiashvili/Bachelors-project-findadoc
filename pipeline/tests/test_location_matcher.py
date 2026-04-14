from __future__ import annotations

from pathlib import Path

import psycopg
import pytest

from pipeline.core.location_matcher import LocationMatcher
from pipeline.core.location_seeder import LocationSeeder


pytestmark = pytest.mark.slow


@pytest.fixture()
def seeded(postgres_container, tmp_path):
    with psycopg.connect(postgres_container, autocommit=True) as conn:
        conn.execute("TRUNCATE doctor_specialty, doctor, location RESTART IDENTITY CASCADE")
    yaml_file = tmp_path / "locations.yaml"
    yaml_file.write_text(
        "- slug: tbilisi\n  name_ka: თბილისი\n  name_en: Tbilisi\n  sort_order: 10\n"
        "- slug: adjara\n  name_ka: აჭარა\n  name_en: Adjara\n  sort_order: 20\n"
        "  cities:\n    - slug: batumi\n      name_ka: ბათუმი\n      name_en: Batumi\n      sort_order: 10\n"
        "- slug: imereti\n  name_ka: იმერეთი\n  name_en: Imereti\n  sort_order: 30\n"
        "  cities:\n    - slug: kutaisi\n      name_ka: ქუთაისი\n      name_en: Kutaisi\n      sort_order: 10\n",
        encoding="utf-8",
    )
    LocationSeeder(dsn=postgres_container, yaml_path=yaml_file).seed()
    yield postgres_container


def _id_of(dsn: str, slug: str) -> int:
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM location WHERE slug=%s", (slug,))
        return cur.fetchone()[0]


def test_match_city_exact_georgian(seeded: str) -> None:
    assert LocationMatcher(dsn=seeded).match_city("ბათუმი") == _id_of(seeded, "batumi")


def test_match_city_exact_english(seeded: str) -> None:
    assert LocationMatcher(dsn=seeded).match_city("Kutaisi") == _id_of(seeded, "kutaisi")


def test_match_city_fuzzy_with_extra_text(seeded: str) -> None:
    assert LocationMatcher(dsn=seeded).match_city("ქ. თბილისი, საბურთალო") == _id_of(seeded, "tbilisi")


def test_match_city_unknown_returns_none(seeded: str) -> None:
    assert LocationMatcher(dsn=seeded).match_city("Atlantis") is None


def test_match_city_blank_returns_none(seeded: str) -> None:
    assert LocationMatcher(dsn=seeded).match_city("  ") is None
