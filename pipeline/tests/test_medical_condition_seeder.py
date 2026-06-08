from __future__ import annotations

import psycopg
import pytest

from pipeline.services.medical_condition_seeder import MedicalConditionSeeder


pytestmark = pytest.mark.slow


@pytest.fixture()
def cond_db(postgres_container, tmp_path):
    with psycopg.connect(postgres_container, autocommit=True) as conn:
        conn.execute(
            "TRUNCATE condition_synonym, condition_specialty, medical_condition, doctor_specialty, specialty RESTART IDENTITY CASCADE"
        )
        conn.execute(
            "INSERT INTO specialty (slug, name_ka, name_en) VALUES ('cardiology','კარდიოლოგია','Cardiology')"
        )
    yield postgres_container


def _yaml(tmp_path, text):
    p = tmp_path / "conditions.yaml"
    p.write_text(text, encoding="utf-8")
    return p


def test_seeds_condition_and_mapping(cond_db, tmp_path):
    y = _yaml(
        tmp_path,
        "- slug: hypertension\n  name_ka: ჰიპერტენზია\n  name_en: Hypertension\n  specialties: [cardiology]\n",
    )
    MedicalConditionSeeder(dsn=cond_db, yaml_path=y).seed()
    with psycopg.connect(cond_db) as conn, conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM medical_condition WHERE slug='hypertension'")
        assert cur.fetchone()[0] == 1
        cur.execute(
            "SELECT count(*) FROM condition_specialty cs "
            "JOIN medical_condition mc ON mc.id=cs.condition_id "
            "JOIN specialty s ON s.id=cs.specialty_id "
            "WHERE mc.slug='hypertension' AND s.slug='cardiology'"
        )
        assert cur.fetchone()[0] == 1


def test_idempotent_and_skips_unknown_specialty(cond_db, tmp_path):
    y = _yaml(
        tmp_path,
        "- slug: x\n  name_ka: ხ\n  name_en: X\n  specialties: [cardiology, nonexistent]\n",
    )
    MedicalConditionSeeder(dsn=cond_db, yaml_path=y).seed()
    MedicalConditionSeeder(dsn=cond_db, yaml_path=y).seed()
    with psycopg.connect(cond_db) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM condition_specialty cs "
            "JOIN medical_condition mc ON mc.id=cs.condition_id WHERE mc.slug='x'"
        )
        assert cur.fetchone()[0] == 1  # only cardiology resolved; nonexistent skipped; no duplicates


def test_seeds_synonyms_with_language_tags(cond_db, tmp_path):
    y = _yaml(
        tmp_path,
        "- slug: hypertension\n"
        "  name_ka: ჰიპერტენზია\n"
        "  name_en: Hypertension\n"
        "  specialties: [cardiology]\n"
        "  synonyms_en: [high blood pressure, HTN, high blood pressure]\n"
        "  synonyms_ka: [მაღალი წნევა, '']\n",
    )
    MedicalConditionSeeder(dsn=cond_db, yaml_path=y).seed()
    MedicalConditionSeeder(dsn=cond_db, yaml_path=y).seed()  # idempotent
    with psycopg.connect(cond_db) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT lang, term FROM condition_synonym cy "
            "JOIN medical_condition mc ON mc.id = cy.condition_id "
            "WHERE mc.slug='hypertension' ORDER BY lang, term"
        )
        rows = cur.fetchall()
    assert ("en", "HTN") in rows
    assert ("en", "high blood pressure") in rows
    assert ("ka", "მაღალი წნევა") in rows
    assert all(term.strip() for _, term in rows)          # blanks skipped
    assert len(rows) == len(set(rows))                    # case-insensitive dedup, no dupes
