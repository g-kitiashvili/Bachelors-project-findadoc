from __future__ import annotations

import psycopg
import pytest

from pipeline.core.persister import Persister
from pipeline.core.record import DoctorRecord
from pipeline.core.specialty_matcher import SpecialtyMatcher
from pipeline.core.translit import normalize


@pytest.fixture()
def persister_db(postgres_container):
    with psycopg.connect(postgres_container, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE doctor_specialty, doctor, specialty RESTART IDENTITY CASCADE")
        cur.execute(
            "INSERT INTO specialty (slug, name_ka, name_en, sort_order) VALUES "
            "('cardiology', 'კარდიოლოგია', 'Cardiology', 10), "
            "('neurology', 'ნევროლოგია', 'Neurology', 70)"
        )
    yield postgres_container


def test_full_scrape_persists_doctor_and_doctor_specialty(persister_db: str) -> None:
    matcher = SpecialtyMatcher(dsn=persister_db)
    persister = Persister(persister_db, specialty_matcher=matcher)

    record = DoctorRecord(
        source="aversi",
        source_url="https://example.com/doc/giorgi",
        full_name_ka="გიორგი ცინცაძე",
        specialty_ka="კარდიოლოგია",
        specialty_en="Cardiology",
    )
    record = normalize(record)
    persister.upsert(record)

    with psycopg.connect(persister_db) as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT s.slug, ds.is_primary
            FROM doctor_specialty ds
            JOIN specialty s ON s.id = ds.specialty_id
            JOIN doctor d ON d.id = ds.doctor_id
            WHERE d.full_name_ka = 'გიორგი ცინცაძე'
            """
        )
        rows = cur.fetchall()
        assert rows == [("cardiology", True)]


def test_unmatched_specialty_token_leaves_doctor_specialty_empty(persister_db: str) -> None:
    matcher = SpecialtyMatcher(dsn=persister_db)
    persister = Persister(persister_db, specialty_matcher=matcher)

    record = DoctorRecord(
        source="aversi",
        source_url="https://example.com/doc/unmapped",
        full_name_ka="ანა ერაძე",
        specialty_ka="completely-unmatched-string",
    )
    record = normalize(record)
    persister.upsert(record)

    with psycopg.connect(persister_db) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM doctor_specialty ds JOIN doctor d ON d.id = ds.doctor_id "
            "WHERE d.full_name_ka = 'ანა ერაძე'"
        )
        assert cur.fetchone()[0] == 0


def test_compound_specialty_writes_primary_and_secondary(persister_db: str) -> None:
    matcher = SpecialtyMatcher(dsn=persister_db)
    persister = Persister(persister_db, specialty_matcher=matcher)

    record = DoctorRecord(
        source="aversi",
        source_url="https://example.com/doc/luka",
        full_name_ka="ლუკა ჯავახიშვილი",
        specialty_ka="კარდიოლოგია, ნევროლოგია",
        specialty_en="Cardiology, Neurology",
    )
    record = normalize(record)
    persister.upsert(record)

    with psycopg.connect(persister_db) as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT s.slug, ds.is_primary
            FROM doctor_specialty ds
            JOIN specialty s ON s.id = ds.specialty_id
            JOIN doctor d ON d.id = ds.doctor_id
            WHERE d.full_name_ka = 'ლუკა ჯავახიშვილი'
            ORDER BY ds.is_primary DESC, s.sort_order ASC
            """
        )
        rows = cur.fetchall()
        assert rows == [("cardiology", True), ("neurology", False)]


def test_first_token_unmapped_still_marks_a_primary(persister_db: str) -> None:
    matcher = SpecialtyMatcher(dsn=persister_db)
    persister = Persister(persister_db, specialty_matcher=matcher)

    record = DoctorRecord(
        source="aversi",
        source_url="https://example.com/doc/beka",
        full_name_ka="ბექა ბაკურაძე",
        specialty_ka="უცნობი, კარდიოლოგია",
    )
    record = normalize(record)
    persister.upsert(record)

    with psycopg.connect(persister_db) as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT s.slug, ds.is_primary
            FROM doctor_specialty ds
            JOIN specialty s ON s.id = ds.specialty_id
            JOIN doctor d ON d.id = ds.doctor_id
            WHERE d.full_name_ka = 'ბექა ბაკურაძე'
            """
        )
        assert cur.fetchone() == ("cardiology", True)
