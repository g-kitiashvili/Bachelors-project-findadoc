from __future__ import annotations

import psycopg
import pytest

from pipeline.core.brand_linker import BrandLinkingPass

pytestmark = pytest.mark.slow

_YAML = (
    "- slug: aversi\n  name_en: Aversi\n  name_ka: ავერსი\n  match_ka: [ავერსი]\n"
    "- slug: new-hospitals\n  name_en: New Hospitals\n  name_ka: ნიუ ჰოსპიტალსი\n  match_ka: [ნიუ ჰოსპიტალს]\n"
    "- slug: new-vision\n  name_en: New Vision\n  name_ka: ნიუ ვიჟენ\n  match_ka: [ნიუ ვიჟენ]\n"
    "- slug: davit-tatishvili\n  name_en: Davit Tatishvili\n  name_ka: დავით ტატიშვილი\n  match_ka: [დავით ტატიშვილ]\n"
)


@pytest.fixture()
def brand_db(postgres_container):
    with psycopg.connect(postgres_container, autocommit=True) as conn:
        conn.execute("TRUNCATE clinic_brand, doctor_clinic, clinic RESTART IDENTITY CASCADE")
        conn.execute(
            "INSERT INTO clinic (slug, name_ka, name_en, last_source_url, status) VALUES "
            "('a1','ავერსის კლინიკა','Aversi Clinic','https://t/a1','ACTIVE'),"
            "('a2','ავერსი – ისნის ფილიალი','Aversi - Isani Branch','https://t/a2','ACTIVE'),"
            "('nh','ნიუ ჰოსპიტალსი','New Hospitals','https://t/nh','ACTIVE'),"
            "('nv','ნიუ ვიჟენ საუნივერსიტეტო ჰოსპიტალი','New Vision University Hospital','https://t/nv','ACTIVE'),"
            "('dt','დავით ტატიშვილის ჯანმრთელობის ცენტრი','Davit Tatishvili Health Center','https://t/dt','ACTIVE'),"
            "('da','დავით აბულაძის კლინიკა','Davit Abuladze Clinic','https://t/da','ACTIVE'),"
            "('solo','ცისფერი კლინიკა','Blue Clinic','https://t/solo','ACTIVE')"
        )
    yield postgres_container


def _yaml(tmp_path, text):
    p = tmp_path / "brands.yaml"
    p.write_text(text, encoding="utf-8")
    return p


def _brand_of(dsn, clinic_slug):
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT cb.slug FROM clinic c LEFT JOIN clinic_brand cb ON cb.id=c.brand_id WHERE c.slug=%s",
            (clinic_slug,),
        )
        return cur.fetchone()[0]


def test_links_clinics_by_ka_prefix(brand_db, tmp_path):
    BrandLinkingPass(dsn=brand_db, yaml_path=_yaml(tmp_path, _YAML)).run()
    assert _brand_of(brand_db, "a1") == "aversi"
    assert _brand_of(brand_db, "a2") == "aversi"


def test_distinct_prefixes_avoid_false_merges(brand_db, tmp_path):
    BrandLinkingPass(dsn=brand_db, yaml_path=_yaml(tmp_path, _YAML)).run()
    assert _brand_of(brand_db, "nh") == "new-hospitals"
    assert _brand_of(brand_db, "nv") == "new-vision"
    assert _brand_of(brand_db, "dt") == "davit-tatishvili"
    assert _brand_of(brand_db, "da") is None


def test_unbranded_null_and_idempotent(brand_db, tmp_path):
    y = _yaml(tmp_path, _YAML)
    BrandLinkingPass(dsn=brand_db, yaml_path=y).run()
    BrandLinkingPass(dsn=brand_db, yaml_path=y).run()
    assert _brand_of(brand_db, "solo") is None
    with psycopg.connect(brand_db) as conn, conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM clinic_brand")
        assert cur.fetchone()[0] == 4
