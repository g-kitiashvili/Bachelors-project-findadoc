from __future__ import annotations

import psycopg
import pytest

from pipeline.core.persister import Persister
from pipeline.core.record import ClinicRef, DoctorRecord
from pipeline.core.translit import normalize


@pytest.fixture()
def clinic_db(postgres_container):
    with psycopg.connect(postgres_container, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute(
            "TRUNCATE doctor_clinic, doctor_specialty, doctor, clinic RESTART IDENTITY CASCADE"
        )
    yield postgres_container


@pytest.mark.slow
def test_upsert_persists_clinics_and_links(clinic_db: str) -> None:
    persister = Persister(clinic_db)

    record = DoctorRecord(
        source="newhospitals",
        source_url="https://example.com/doc/giorgi",
        full_name_ka="გიორგი ცინცაძე",
        clinics=(
            ClinicRef(
                source_url="https://example.com/clinic/new-hospitals",
                name_ka="ნიუ ჰოსპიტალსი",
                address="თბილისი, ყაზბეგის გამზირი 16",
                phone="+995322000000",
            ),
            ClinicRef(
                source_url="https://example.com/clinic/vivo-medical",
                name_ka="ვივო მედიქალ",
            ),
        ),
    )
    record = normalize(record)
    persister.upsert(record)

    with psycopg.connect(clinic_db) as conn, conn.cursor() as cur:
        cur.execute("SELECT name_ka, name_en FROM clinic ORDER BY id")
        clinics = cur.fetchall()
        assert clinics == [
            ("ნიუ ჰოსპიტალსი", "New Hospitals"),
            ("ვივო მედიქალ", "Vivo Medical"),
        ]

        cur.execute(
            """
            SELECT c.name_en
            FROM doctor_clinic dc
            JOIN clinic c ON c.id = dc.clinic_id
            JOIN doctor d ON d.id = dc.doctor_id
            WHERE d.full_name_ka = 'გიორგი ცინცაძე'
            ORDER BY c.id
            """
        )
        assert cur.fetchall() == [("New Hospitals",), ("Vivo Medical",)]


@pytest.mark.slow
def test_upsert_clinics_is_idempotent_on_rerun(clinic_db: str) -> None:
    persister = Persister(clinic_db)

    record = DoctorRecord(
        source="newhospitals",
        source_url="https://example.com/doc/giorgi",
        full_name_ka="გიორგი ცინცაძე",
        clinics=(
            ClinicRef(
                source_url="https://example.com/clinic/new-hospitals",
                name_ka="ნიუ ჰოსპიტალსი",
            ),
        ),
    )
    record = normalize(record)
    persister.upsert(record)
    persister.upsert(record)

    with psycopg.connect(clinic_db) as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM clinic")
        assert cur.fetchone()[0] == 1
        cur.execute("SELECT COUNT(*) FROM doctor_clinic")
        assert cur.fetchone()[0] == 1
