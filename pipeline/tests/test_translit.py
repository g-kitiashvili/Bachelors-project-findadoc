import pytest
from pipeline.core.translit import mkhedruli_to_latin, slugify, next_slug_candidate, normalize
from pipeline.core.record import DoctorRecord


@pytest.mark.parametrize(
    "ka,expected",
    [
        ("ა", "a"), ("ბ", "b"), ("გ", "g"), ("დ", "d"), ("ე", "e"),
        ("ვ", "v"), ("ზ", "z"), ("თ", "t"), ("ი", "i"), ("კ", "k"),
        ("ლ", "l"), ("მ", "m"), ("ნ", "n"), ("ო", "o"), ("პ", "p"),
        ("ჟ", "zh"), ("რ", "r"), ("ს", "s"), ("ტ", "t"), ("უ", "u"),
        ("ფ", "p"), ("ქ", "k"), ("ღ", "gh"), ("ყ", "q"), ("შ", "sh"),
        ("ჩ", "ch"), ("ც", "ts"), ("ძ", "dz"), ("წ", "ts"), ("ჭ", "ch"),
        ("ხ", "kh"), ("ჯ", "j"), ("ჰ", "h"),
    ],
)
def test_mkhedruli_letter_table(ka, expected):
    assert mkhedruli_to_latin(ka) == expected


def test_mkhedruli_passes_through_non_georgian_chars():
    assert mkhedruli_to_latin("Dr. გიორგი 42") == "Dr. giorgi 42"


def test_mkhedruli_uppercase_georgian_letters_not_expected_but_dont_crash():
    out = mkhedruli_to_latin("Ⴀ")
    assert isinstance(out, str)


def test_slugify_basic():
    assert slugify("Giorgi Tsintsadze") == "giorgi-tsintsadze"


def test_slugify_georgian_name():
    assert slugify("გიორგი ცინცაძე") == "giorgi-tsintsadze"


def test_slugify_collapses_runs_and_strips_edges():
    assert slugify("  Dr.   Giorgi---Tsintsadze, MD!  ") == "dr-giorgi-tsintsadze-md"


def test_slugify_punctuation_only_input_returns_empty_string():
    assert slugify("---!!!") == ""


def test_slugify_idempotent():
    once = slugify("გიორგი ცინცაძე")
    twice = slugify(once)
    assert once == twice


def test_next_slug_candidate_first_attempt_returns_base():
    assert next_slug_candidate("giorgi-tsintsadze", 1) == "giorgi-tsintsadze"


def test_next_slug_candidate_subsequent_attempts_append_suffix():
    assert next_slug_candidate("giorgi-tsintsadze", 2) == "giorgi-tsintsadze-2"
    assert next_slug_candidate("giorgi-tsintsadze", 99) == "giorgi-tsintsadze-99"


def test_next_slug_candidate_rejects_zero_or_negative():
    with pytest.raises(ValueError):
        next_slug_candidate("x", 0)
    with pytest.raises(ValueError):
        next_slug_candidate("x", -1)


def test_next_slug_candidate_rejects_attempt_over_99():
    with pytest.raises(ValueError):
        next_slug_candidate("x", 100)


def _record(**overrides):
    base = {
        "source": "newhospitals",
        "source_url": "https://newhospitals.ge/doctor/x",
        "full_name_ka": "გიორგი ცინცაძე",
    }
    base.update(overrides)
    return DoctorRecord(**base)


def test_normalize_fills_full_name_en_when_missing():
    r = normalize(_record())
    assert r.full_name_en == "Giorgi Tsintsadze"  # title-cased from translit


def test_normalize_keeps_full_name_en_when_present():
    r = normalize(_record(full_name_en="Giorgi Tsintsadze"))
    assert r.full_name_en == "Giorgi Tsintsadze"


def test_normalize_sets_slug_base_from_full_name_ka():
    r = normalize(_record())
    assert r.slug_base == "giorgi-tsintsadze"


def test_normalize_returns_a_new_frozen_record():
    r1 = _record()
    r2 = normalize(r1)
    assert r1 is not r2
    assert r1.full_name_en is None
    assert r2.full_name_en is not None


def test_normalize_is_idempotent():
    r1 = normalize(_record())
    r2 = normalize(r1)
    assert r1 == r2
