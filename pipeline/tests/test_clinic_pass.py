from __future__ import annotations

import psycopg
import pytest

from pipeline.services.clinic_pass import ClinicPass

pytestmark = pytest.mark.slow


@pytest.fixture()
def clinic_pass_db(postgres_container):
    with psycopg.connect(postgres_container, autocommit=True) as conn:
        conn.execute("TRUNCATE doctor_clinic, clinic RESTART IDENTITY CASCADE")
    yield postgres_container


def _insert(cur, slug, name_ka, name_en, url, address=None):
    cur.execute(
        "INSERT INTO clinic (slug, name_ka, name_en, address, last_source_url, last_updated_at, status) "
        "VALUES (%s,%s,%s,%s,%s, now(), 'ACTIVE') RETURNING id",
        (slug, name_ka, name_en, address, url),
    )
    return cur.fetchone()[0]


def test_prefixes_aversi_branch_and_romanizes_address(clinic_pass_db):
    with psycopg.connect(clinic_pass_db, autocommit=True) as conn, conn.cursor() as cur:
        _insert(cur, "central", "ცენტრალური ფილიალი | ლაბორატორია", "Central Branch",
                "https://dashboard.aversiclinic.ge/branch/5", address="ვაჟა-ფშაველას გამზ. 27")
    ClinicPass(clinic_pass_db).run()
    with psycopg.connect(clinic_pass_db) as conn, conn.cursor() as cur:
        cur.execute("SELECT name_ka, name_en, address_en FROM clinic WHERE slug='central'")
        ka, en, addr_en = cur.fetchone()
    assert ka == "ავერსი – ცენტრალური ფილიალი"
    assert en == "Aversi – Central Branch"
    assert "Ave." in addr_en


def test_deactivates_vipmed_role_phrase_keeps_real_clinic(clinic_pass_db):
    with psycopg.connect(clinic_pass_db, autocommit=True) as conn, conn.cursor() as cur:
        _insert(cur, "role", "ავერსის კლინიკის ექიმი",
                "Oncologist of the Central Branch of Aversi Clinic", "https://vipmed.ge/clinic/x")
        _insert(cur, "real", "თოდუას კლინიკა", "Todua Clinic", "https://vipmed.ge/clinic/todua")
    ClinicPass(clinic_pass_db).run()
    with psycopg.connect(clinic_pass_db) as conn, conn.cursor() as cur:
        cur.execute("SELECT status FROM clinic WHERE slug='role'")
        assert cur.fetchone()[0] == "INACTIVE"
        cur.execute("SELECT status FROM clinic WHERE slug='real'")
        assert cur.fetchone()[0] == "ACTIVE"


def test_does_not_deactivate_official_clinic(clinic_pass_db):
    # is_role_phrase is only applied to aggregator hosts; an official name is never dropped.
    with psycopg.connect(clinic_pass_db, autocommit=True) as conn, conn.cursor() as cur:
        _insert(cur, "evex", "ევექსი", "Evex Vaja-Pshavela Clinic", "https://admin.evex.ge/c/1")
    ClinicPass(clinic_pass_db).run()
    with psycopg.connect(clinic_pass_db) as conn, conn.cursor() as cur:
        cur.execute("SELECT status FROM clinic WHERE slug='evex'")
        assert cur.fetchone()[0] == "ACTIVE"
