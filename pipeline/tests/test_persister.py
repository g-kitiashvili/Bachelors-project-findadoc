import psycopg
import pytest

from pipeline.core.persister import Persister
from pipeline.core.record import DoctorRecord
from pipeline.core.translit import normalize


pytestmark = pytest.mark.slow


def _normalized(**overrides) -> DoctorRecord:
    base = {
        "source": "newhospitals",
        "source_url": "https://newhospitals.ge/doctor/x1",
        "full_name_ka": "გიორგი ცინცაძე",
    }
    base.update(overrides)
    return normalize(DoctorRecord(**base))


def _count(dsn: str) -> int:
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM doctor")
        return cur.fetchone()[0]


def test_upsert_inserts_new_row(clean_doctor_table):
    p = Persister(clean_doctor_table)
    action = p.upsert(_normalized())
    assert action == "inserted"
    assert _count(clean_doctor_table) == 1


def test_upsert_returns_action_inserted_then_updated(clean_doctor_table):
    p = Persister(clean_doctor_table)
    r1 = _normalized(full_name_ka="გიორგი ცინცაძე")
    r2 = _normalized(full_name_ka="გიორგი ცინცაძე-მარკოვი")  # same source_url
    assert p.upsert(r1) == "inserted"
    assert p.upsert(r2) == "updated"
    assert _count(clean_doctor_table) == 1


def test_upsert_advances_last_updated_at_on_rescrape(clean_doctor_table):
    p = Persister(clean_doctor_table)
    r = _normalized()
    p.upsert(r)
    with psycopg.connect(clean_doctor_table) as conn, conn.cursor() as cur:
        cur.execute("SELECT last_updated_at FROM doctor WHERE last_source_url=%s", (str(r.source_url),))
        t1 = cur.fetchone()[0]
    p.upsert(r)
    with psycopg.connect(clean_doctor_table) as conn, conn.cursor() as cur:
        cur.execute("SELECT last_updated_at FROM doctor WHERE last_source_url=%s", (str(r.source_url),))
        t2 = cur.fetchone()[0]
    assert t2 >= t1


def test_upsert_keeps_slug_stable_on_rescrape(clean_doctor_table):
    p = Persister(clean_doctor_table)
    r = _normalized()
    p.upsert(r)
    with psycopg.connect(clean_doctor_table) as conn, conn.cursor() as cur:
        cur.execute("SELECT slug FROM doctor WHERE last_source_url=%s", (str(r.source_url),))
        slug_first = cur.fetchone()[0]
    p.upsert(_normalized(full_name_ka="ბ ბ ბ"))
    with psycopg.connect(clean_doctor_table) as conn, conn.cursor() as cur:
        cur.execute("SELECT slug FROM doctor WHERE last_source_url=%s", (str(r.source_url),))
        slug_after = cur.fetchone()[0]
    assert slug_first == slug_after


def test_upsert_assigns_dash_suffix_on_slug_collision(clean_doctor_table):
    p = Persister(clean_doctor_table)
    r1 = _normalized(source_url="https://newhospitals.ge/doctor/a")
    r2 = _normalized(source_url="https://newhospitals.ge/doctor/b")  # same name, different URL → collision
    p.upsert(r1)
    p.upsert(r2)
    with psycopg.connect(clean_doctor_table) as conn, conn.cursor() as cur:
        cur.execute("SELECT slug FROM doctor ORDER BY id")
        slugs = [row[0] for row in cur.fetchall()]
    assert slugs == ["giorgi-tsintsadze", "giorgi-tsintsadze-2"]


def test_upsert_raises_on_unnormalized_record(clean_doctor_table):
    p = Persister(clean_doctor_table)
    bad = DoctorRecord(
        source="newhospitals",
        source_url="https://newhospitals.ge/doctor/x",
        full_name_ka="გიორგი",
    )  # no full_name_en, no slug_base
    with pytest.raises(AssertionError):
        p.upsert(bad)


def test_upsert_round_trips_specialty(clean_doctor_table):
    p = Persister(clean_doctor_table)
    r = _normalized(
        source_url="https://newhospitals.ge/doctor/x2",
        specialty_ka="გასტროენტეროლოგი",
        specialty_en="Gastroenterologist",
    )
    p.upsert(r)
    with psycopg.connect(clean_doctor_table) as conn, conn.cursor() as cur:
        cur.execute("SELECT specialty_ka, specialty_en FROM doctor WHERE last_source_url=%s", (str(r.source_url),))
        ka, en = cur.fetchone()
    assert ka == "გასტროენტეროლოგი"
    assert en == "Gastroenterologist"
