import pytest
from pydantic import ValidationError
from pipeline.core.record import DoctorRecord


def _kwargs(**overrides):
    base = {
        "source": "newhospitals",
        "source_url": "https://newhospitals.ge/doctor/x",
        "full_name_ka": "გიორგი ცინცაძე",
    }
    base.update(overrides)
    return base


def test_record_minimum_required_fields():
    r = DoctorRecord(**_kwargs())
    assert r.source == "newhospitals"
    assert r.full_name_ka == "გიორგი ცინცაძე"
    assert r.full_name_en is None
    assert r.slug_base is None
    assert r.gender is None


def test_record_is_frozen():
    r = DoctorRecord(**_kwargs())
    with pytest.raises(ValidationError):
        r.full_name_ka = "მუტაცია"


def test_record_rejects_missing_required():
    with pytest.raises(ValidationError):
        DoctorRecord(source="newhospitals", source_url="https://x", full_name_ka="")


def test_record_rejects_bad_url():
    with pytest.raises(ValidationError):
        DoctorRecord(**_kwargs(source_url="not-a-url"))


def test_record_accepts_full_payload():
    r = DoctorRecord(**_kwargs(
        full_name_en="Giorgi Tsintsadze",
        photo_url="https://cdn.example/g.jpg",
        bio_ka="...",
        bio_en="...",
        gender="male",
        slug_base="giorgi-tsintsadze",
    ))
    assert r.full_name_en == "Giorgi Tsintsadze"
    assert r.gender == "male"
    assert r.slug_base == "giorgi-tsintsadze"


def test_record_rejects_bad_gender():
    with pytest.raises(ValidationError):
        DoctorRecord(**_kwargs(gender="invalid"))


def test_record_with_updated_fields_returns_new_instance():
    r = DoctorRecord(**_kwargs())
    r2 = r.model_copy(update={"full_name_en": "Giorgi Tsintsadze"})
    assert r.full_name_en is None
    assert r2.full_name_en == "Giorgi Tsintsadze"
    assert r is not r2


def test_record_accepts_specialty():
    r = DoctorRecord(**_kwargs(specialty_ka="გასტროენტეროლოგი", specialty_en="Gastroenterologist"))
    assert r.specialty_ka == "გასტროენტეროლოგი"
    assert r.specialty_en == "Gastroenterologist"
