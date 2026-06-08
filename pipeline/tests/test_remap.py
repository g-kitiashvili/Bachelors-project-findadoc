from __future__ import annotations

import psycopg
import pytest

from pipeline.domain.non_providers import NonProviderList, _Rule
from pipeline.services.remapper import Remapper
from pipeline.services.specialty_matcher import SpecialtyMatcher
from pipeline.domain.taxonomy import normalize_alias


@pytest.fixture()
def remap_db(postgres_container):
    with psycopg.connect(postgres_container, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE doctor_specialty, doctor, specialty RESTART IDENTITY CASCADE")
        cur.execute(
            "INSERT INTO specialty (slug, name_ka, name_en, sort_order) VALUES "
            "('cardiology', 'კარდიოლოგია', 'Cardiology', 10)"
        )
        cur.execute(
            "INSERT INTO doctor (slug, full_name_ka, full_name_en, specialty_ka, "
            "treats_children, treats_adults, last_source_url, last_updated_at, status) VALUES "
            "('a', 'ა ა', 'A A', 'ოჯახის ექიმი', false, true, 'https://x/a', NOW(), 'ACTIVE'), "
            "('b', 'ბ ბ', 'B B', 'კლინიკური მენეჯერი', false, true, 'https://x/b', NOW(), 'ACTIVE')"
        )
    yield postgres_container


def _slugs_for(dsn: str, full_name_ka: str) -> list[str]:
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT s.slug FROM doctor_specialty ds JOIN specialty s ON s.id = ds.specialty_id "
            "JOIN doctor d ON d.id = ds.doctor_id WHERE d.full_name_ka = %s ORDER BY s.slug",
            (full_name_ka,),
        )
        return [r[0] for r in cur.fetchall()]


def test_remap_maps_aliased_doctor(remap_db: str) -> None:
    matcher = SpecialtyMatcher(dsn=remap_db, aliases={normalize_alias("ოჯახის ექიმი"): "cardiology"})
    stats = Remapper(remap_db, matcher=matcher).remap_all()
    assert _slugs_for(remap_db, "ა ა") == ["cardiology"]
    assert stats.mapped_after >= stats.mapped_before


def test_remap_deactivates_non_provider(remap_db: str) -> None:
    matcher = SpecialtyMatcher(dsn=remap_db)
    non_providers = NonProviderList([_Rule(text=normalize_alias("კლინიკური მენეჯერი"), substring=False)])
    Remapper(remap_db, matcher=matcher, non_providers=non_providers).remap_all()
    with psycopg.connect(remap_db) as conn, conn.cursor() as cur:
        cur.execute("SELECT status FROM doctor WHERE full_name_ka = 'ბ ბ'")
        assert cur.fetchone() == ("INACTIVE",)


def test_remap_is_idempotent(remap_db: str) -> None:
    matcher = SpecialtyMatcher(dsn=remap_db, aliases={normalize_alias("ოჯახის ექიმი"): "cardiology"})
    Remapper(remap_db, matcher=matcher).remap_all()
    Remapper(remap_db, matcher=matcher).remap_all()
    assert _slugs_for(remap_db, "ა ა") == ["cardiology"]


def test_remap_reactivates_mappable_doctor(remap_db: str) -> None:
    with psycopg.connect(remap_db, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute("UPDATE doctor SET status='INACTIVE' WHERE full_name_ka='ა ა'")
    matcher = SpecialtyMatcher(dsn=remap_db, aliases={normalize_alias("ოჯახის ექიმი"): "cardiology"})
    Remapper(remap_db, matcher=matcher).remap_all()
    with psycopg.connect(remap_db) as conn, conn.cursor() as cur:
        cur.execute("SELECT status FROM doctor WHERE full_name_ka='ა ა'")
        assert cur.fetchone() == ("ACTIVE",)


def test_remap_rolls_back_on_regression(remap_db: str) -> None:
    from pipeline.services.remapper import RemapRegression

    with psycopg.connect(remap_db, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO doctor_specialty (doctor_id, specialty_id, is_primary) "
            "SELECT d.id, s.id, true FROM doctor d, specialty s "
            "WHERE d.full_name_ka='ა ა' AND s.slug='cardiology'"
        )
    matcher = SpecialtyMatcher(dsn=remap_db, aliases={})  # 'ოჯახის ექიმი' won't map -> regression
    with pytest.raises(RemapRegression):
        Remapper(remap_db, matcher=matcher).remap_all()
    assert _slugs_for(remap_db, "ა ა") == ["cardiology"]  # preserved by rollback
