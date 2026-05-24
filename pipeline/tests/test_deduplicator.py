from __future__ import annotations

import psycopg
import pytest

from pipeline.core.deduplicator import Deduplicator, DedupRegression

pytestmark = pytest.mark.slow


@pytest.fixture()
def dedup_db(postgres_container):
    with psycopg.connect(postgres_container, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute(
            "TRUNCATE doctor_specialty, doctor_clinic, clinic, doctor, specialty "
            "RESTART IDENTITY CASCADE"
        )
        cur.execute(
            "INSERT INTO specialty (slug, name_ka, name_en, sort_order) VALUES "
            "('cardiology','კარდიოლოგია','Cardiology',10),('neurology','ნევროლოგია','Neurology',70)"
        )
    yield postgres_container


def _insert_doctor(cur, slug, name_en, name_ka, src, specialty_slug, photo=None):
    cur.execute(
        "INSERT INTO doctor (slug, full_name_ka, full_name_en, photo_url, last_source_url, "
        "last_updated_at, status) VALUES (%s,%s,%s,%s,%s, now(), 'ACTIVE') RETURNING id",
        (slug, name_ka, name_en, photo, f"https://{src}/{slug}"),
    )
    did = cur.fetchone()[0]
    if specialty_slug:
        cur.execute(
            "INSERT INTO doctor_specialty (doctor_id, specialty_id, is_primary) "
            "SELECT %s, id, true FROM specialty WHERE slug=%s",
            (did, specialty_slug),
        )
    return did


def _status(dsn, slug):
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute("SELECT status, merged_into_id FROM doctor WHERE slug=%s", (slug,))
        return cur.fetchone()


def test_merges_exact_name_shared_specialty_across_sources(dedup_db):
    with psycopg.connect(dedup_db, autocommit=True) as conn, conn.cursor() as cur:
        a = _insert_doctor(cur, "arch-evex", "Archil Test", "არჩილ ტესტი", "evex.ge", "cardiology", photo="p")
        _insert_doctor(cur, "arch-cmc", "Archil Test", "არჩილ ტესტი", "cmc.ge", "cardiology")
    Deduplicator(dedup_db).run()
    assert _status(dedup_db, "arch-evex") == ("ACTIVE", None)
    st, into = _status(dedup_db, "arch-cmc")
    assert st == "MERGED" and into == a


def test_merges_when_only_ka_name_matches(dedup_db):
    with psycopg.connect(dedup_db, autocommit=True) as conn, conn.cursor() as cur:
        _insert_doctor(cur, "k1", "Nino Sharashenidze", "ნინო ტესტი", "evex.ge", "cardiology")
        _insert_doctor(cur, "k2", "Nino Sharasenidze",  "ნინო ტესტი", "cmc.ge",  "cardiology")
    Deduplicator(dedup_db).run()
    statuses = {_status(dedup_db, "k1")[0], _status(dedup_db, "k2")[0]}
    assert statuses == {"ACTIVE", "MERGED"}


def test_does_not_merge_near_spelling(dedup_db):
    with psycopg.connect(dedup_db, autocommit=True) as conn, conn.cursor() as cur:
        _insert_doctor(cur, "s1", "Archil Sharashenidze", "ა ერთი", "evex.ge", "cardiology")
        _insert_doctor(cur, "s2", "Archil Sharasenidze",  "ა ორი",  "cmc.ge",  "cardiology")
    Deduplicator(dedup_db).run()
    assert _status(dedup_db, "s1")[0] == "ACTIVE"
    assert _status(dedup_db, "s2")[0] == "ACTIVE"


def test_merges_within_source_duplicate_sharing_specialty(dedup_db):
    # a source can list the same person twice; sharing a specialty, they still merge
    with psycopg.connect(dedup_db, autocommit=True) as conn, conn.cursor() as cur:
        _insert_doctor(cur, "w1", "Giorgi Same", "გ ერთი", "evex.ge", "cardiology")
        _insert_doctor(cur, "w2", "Giorgi Same", "გ ორი",  "evex.ge", "cardiology")
        _insert_doctor(cur, "w3", "Giorgi Same", "გ სამი",  "cmc.ge",  "cardiology")
    Deduplicator(dedup_db).run()
    statuses = sorted(_status(dedup_db, s)[0] for s in ("w1", "w2", "w3"))
    assert statuses == ["ACTIVE", "MERGED", "MERGED"]


def test_does_not_merge_different_specialty(dedup_db):
    with psycopg.connect(dedup_db, autocommit=True) as conn, conn.cursor() as cur:
        _insert_doctor(cur, "d1", "Lana Test", "ლ ერთი", "evex.ge", "cardiology")
        _insert_doctor(cur, "d2", "Lana Test", "ლ ორი",  "cmc.ge",  "neurology")
    Deduplicator(dedup_db).run()
    assert _status(dedup_db, "d1")[0] == "ACTIVE"
    assert _status(dedup_db, "d2")[0] == "ACTIVE"


def test_idempotent_and_reversible(dedup_db):
    with psycopg.connect(dedup_db, autocommit=True) as conn, conn.cursor() as cur:
        _insert_doctor(cur, "i1", "Mariam Test", "მ ერთი", "evex.ge", "cardiology", photo="p")
        _insert_doctor(cur, "i2", "Mariam Test", "მ ერთი", "cmc.ge",  "cardiology")
    Deduplicator(dedup_db).run()
    Deduplicator(dedup_db).run()
    assert _status(dedup_db, "i1") == ("ACTIVE", None)
    assert _status(dedup_db, "i2")[0] == "MERGED"
    with psycopg.connect(dedup_db) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM doctor_specialty ds JOIN doctor d ON d.id=ds.doctor_id "
            "WHERE d.slug='i1'"
        )
        assert cur.fetchone()[0] == 1


def test_regression_rolls_back(dedup_db):
    with psycopg.connect(dedup_db, autocommit=True) as conn, conn.cursor() as cur:
        for i in range(10):
            _insert_doctor(cur, f"r{i}", "Same Name", "ს ს", f"src{i}.ge", "cardiology")
    with pytest.raises(DedupRegression):
        Deduplicator(dedup_db, max_merge_fraction=0.4).run()
    with psycopg.connect(dedup_db) as conn, conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM doctor WHERE status='MERGED'")
        assert cur.fetchone()[0] == 0


def _insert_clinic(cur, slug, name_en, src, phone=None, website=None, address=None):
    cur.execute(
        "INSERT INTO clinic (slug, name_ka, name_en, phone, website, address, last_source_url, "
        "last_updated_at, status) VALUES (%s,%s,%s,%s,%s,%s,%s, now(), 'ACTIVE') RETURNING id",
        (slug, name_en, name_en, phone, website, address, f"https://{src}/{slug}"),
    )
    return cur.fetchone()[0]


def test_merges_clinic_same_name_across_sources(dedup_db):
    # Aggregators relist a clinic with no phone/website to correlate on; matching on
    # the shared name across distinct sources is enough to merge.
    with psycopg.connect(dedup_db, autocommit=True) as conn, conn.cursor() as cur:
        _insert_clinic(cur, "alpha-evex", "Alpha Clinic", "evex.ge")
        c2 = _insert_clinic(cur, "alpha-tsamali", "Alpha Clinic", "tsamali.ge")
        d = _insert_doctor(cur, "dc1", "Doc One", "დ ერთი", "tsamali.ge", "cardiology")
        cur.execute("INSERT INTO doctor_clinic (doctor_id, clinic_id) VALUES (%s,%s)", (d, c2))
    Deduplicator(dedup_db).run()
    with psycopg.connect(dedup_db) as conn, conn.cursor() as cur:
        cur.execute("SELECT status FROM clinic WHERE slug='alpha-evex'")
        assert cur.fetchone()[0] == "ACTIVE"
        cur.execute("SELECT status FROM clinic WHERE slug='alpha-tsamali'")
        assert cur.fetchone()[0] == "MERGED"
        cur.execute(
            "SELECT count(*) FROM doctor_clinic dc JOIN clinic c ON c.id=dc.clinic_id "
            "WHERE c.status='ACTIVE' AND dc.doctor_id=%s", (d,))
        assert cur.fetchone()[0] >= 1


def test_clinic_merge_prefers_official_and_enriches(dedup_db):
    # Official source is canonical even when the aggregator copy is more complete;
    # the official record absorbs the aggregator's address.
    with psycopg.connect(dedup_db, autocommit=True) as conn, conn.cursor() as cur:
        _insert_clinic(cur, "beta-newhosp", "Beta Hospital", "newhospitals.ge")
        _insert_clinic(cur, "beta-tsamali", "Beta Hospital", "tsamali.ge", address="Krtsanisi St. 12")
    Deduplicator(dedup_db).run()
    with psycopg.connect(dedup_db) as conn, conn.cursor() as cur:
        cur.execute("SELECT status, address FROM clinic WHERE slug='beta-newhosp'")
        status, address = cur.fetchone()
        assert status == "ACTIVE"
        assert address == "Krtsanisi St. 12"
        cur.execute("SELECT status FROM clinic WHERE slug='beta-tsamali'")
        assert cur.fetchone()[0] == "MERGED"


def test_merges_same_name_within_one_source(dedup_db):
    # A source can list one clinic under near-identical names for different doctors;
    # they collapse to a single entry.
    with psycopg.connect(dedup_db, autocommit=True) as conn, conn.cursor() as cur:
        _insert_clinic(cur, "gamma-1", "Gamma Clinic", "tsamali.ge")
        _insert_clinic(cur, "gamma-2", "Gamma Clinic", "tsamali.ge")
    Deduplicator(dedup_db).run()
    with psycopg.connect(dedup_db) as conn, conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM clinic WHERE status='ACTIVE'")
        assert cur.fetchone()[0] == 1


def test_merges_across_quote_punctuation_differences(dedup_db):
    # vipmed wraps names in curly quotes; the dedup key ignores quotes so the quoted
    # and unquoted copies merge.
    with psycopg.connect(dedup_db, autocommit=True) as conn, conn.cursor() as cur:
        _insert_clinic(cur, "delta-evex", "Delta Clinic", "evex.ge")
        _insert_clinic(cur, "delta-vipmed", "“Delta Clinic”", "vipmed.ge")
    Deduplicator(dedup_db).run()
    with psycopg.connect(dedup_db) as conn, conn.cursor() as cur:
        cur.execute("SELECT status FROM clinic WHERE slug='delta-evex'")
        assert cur.fetchone()[0] == "ACTIVE"
        cur.execute("SELECT status FROM clinic WHERE slug='delta-vipmed'")
        assert cur.fetchone()[0] == "MERGED"
