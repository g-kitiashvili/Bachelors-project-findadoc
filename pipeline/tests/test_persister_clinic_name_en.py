from __future__ import annotations

import psycopg
import pytest

from pipeline.services.persister import Persister
from pipeline.domain.record import ClinicRef, DoctorRecord
from pipeline.domain.translit import normalize


@pytest.fixture()
def clinic_db(postgres_container):
    with psycopg.connect(postgres_container, autocommit=True) as conn:
        conn.execute("TRUNCATE doctor_clinic, doctor_specialty, doctor, clinic RESTART IDENTITY CASCADE")
    yield postgres_container


def _name_en(dsn: str, name_ka: str) -> str:
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute("SELECT name_en FROM clinic WHERE name_ka = %s", (name_ka,))
        return cur.fetchone()[0]


def test_source_name_en_used_verbatim(clinic_db: str) -> None:
    persister = Persister(clinic_db)
    record = normalize(DoctorRecord(
        source="cmc", source_url="https://example.com/d/1", full_name_ka="ა ბ",
        clinics=(ClinicRef(source_url="https://cmchospital.ge", name_ka="კავკასიის მედიცინის ცენტრი",
                           name_en="Caucasus Medical Centre"),),
    ))
    persister.upsert(record)
    assert _name_en(clinic_db, "კავკასიის მედიცინის ცენტრი") == "Caucasus Medical Centre"


def test_address_en_is_romanized(clinic_db: str) -> None:
    persister = Persister(clinic_db)
    record = normalize(DoctorRecord(
        source="tsamali", source_url="https://example.com/d/3", full_name_ka="ა ბ",
        clinics=(ClinicRef(source_url="https://tsamali.ge/klinika/x", name_ka="ტესტ კლინიკა",
                           address="ლუბლიანას ქ. 15"),),
    ))
    persister.upsert(record)
    with psycopg.connect(clinic_db) as conn, conn.cursor() as cur:
        cur.execute("SELECT address_en FROM clinic WHERE name_ka = %s", ("ტესტ კლინიკა",))
        assert cur.fetchone()[0] == "Lublianas St. 15"


def test_missing_name_en_falls_back_to_algorithm(clinic_db: str) -> None:
    persister = Persister(clinic_db)
    record = normalize(DoctorRecord(
        source="tsamali", source_url="https://example.com/d/2", full_name_ka="ა ბ",
        clinics=(ClinicRef(source_url="https://tsamali.ge/klinika/gaguas-klinika", name_ka="გაგუას კლინიკა"),),
    ))
    persister.upsert(record)
    assert _name_en(clinic_db, "გაგუას კლინიკა") == "Gagua Clinic"
