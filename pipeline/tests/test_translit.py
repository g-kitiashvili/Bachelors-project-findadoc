import pytest
from pipeline.domain.translit import kartuli_to_latin, slugify, next_slug_candidate, normalize, clinic_name_to_en
from pipeline.domain.record import DoctorRecord
from pipeline.domain.translit import english_or_none


def test_english_or_none_passes_latin():
    assert english_or_none("Levan Makhaldiani") == "Levan Makhaldiani"


def test_english_or_none_strips_whitespace():
    assert english_or_none("  Aversi Clinic  ") == "Aversi Clinic"


def test_english_or_none_rejects_georgian():
    assert english_or_none("ანა ჯანაშვილი") is None


def test_english_or_none_rejects_mixed():
    assert english_or_none("Aversi ავერსი") is None


def test_english_or_none_handles_empty():
    assert english_or_none(None) is None
    assert english_or_none("   ") is None


@pytest.mark.parametrize("input_,expected", [
    ("ჟორდანიას სამედიცინო ცენტრი", "Zhordania Medical Center"),
    ("თბილისის ცენტრალური საავადმყოფო", "Tbilisi Central Hospital"),
    ("ბოხუას სახელობის კარდიოვასკულარული ცენტრი", "Bokhua Cardiovascular Center"),
    ("გაგუას კლინიკა", "Gagua Clinic"),
    ("ნიუ ჰოსპიტალსი", "New Hospitals"),
    ("ევექსის კლინიკა ვარკეთილში", "Evex Clinic Varketilshi"),
    ("ავერსის კლინიკა", "Aversi Clinic"),
    ("დიაკორი", "Diacor"),
])
def test_clinic_name_translates_common_words_and_transliterates_proper_nouns(input_, expected):
    assert clinic_name_to_en(input_) == expected


def test_clinic_name_override_corrects_incomplete_source_name():
    assert clinic_name_to_en("ინ ვიტრო") == "Innova In Vitro"


@pytest.mark.parametrize("ka,expected", [
    ("ჯეო ჰოსპიტალსი", "Geo Hospitals"),
    ("ინოვა სამედიცინო ცენტრი", "Innova Medical Center"),
    ("ნიუ ვიჟენ საუნივერსიტეტო ჰოსპიტალი", "New Vision University Hospital"),
    ("ჯო ენის სამედიცინო ცენტრი", "JoAnn Medical Center"),
    ("ჯო ენის საუნივერსიტეტო ჰოსპიტალი", "JoAnn University Hospital"),
])
def test_brand_romanization_fixes(ka, expected):
    assert clinic_name_to_en(ka) == expected


def test_clinic_genitive_named_after():
    assert clinic_name_to_en("ჟორდანიას სამედიცინო ცენტრი") == "Zhordania Medical Center"


def test_clinic_genitive_dze_surname():
    assert clinic_name_to_en("აბულაძის კლინიკა") == "Abuladze Clinic"


def test_clinic_genitive_place():
    assert clinic_name_to_en("თბილისის ცენტრალური საავადმყოფო") == "Tbilisi Central Hospital"


def test_clinic_brand_preserved():
    assert clinic_name_to_en("ავერსის კლინიკა") == "Aversi Clinic"


def test_clinic_plain_word():
    assert clinic_name_to_en("გაგუას კლინიკა") == "Gagua Clinic"


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
def test_kartuli_letter_table(ka, expected):
    assert kartuli_to_latin(ka) == expected


def test_kartuli_passes_through_non_georgian_chars():
    assert kartuli_to_latin("Dr. გიორგი 42") == "Dr. giorgi 42"


def test_kartuli_uppercase_georgian_letters_not_expected_but_dont_crash():
    out = kartuli_to_latin("Ⴀ")
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


def test_normalize_collapses_internal_double_spaces_in_names():
    r = normalize(_record(full_name_ka="ზაზა  კაციტაძე", full_name_en="Zaza  Katsitadze"))
    assert r.full_name_ka == "ზაზა კაციტაძე"
    assert r.full_name_en == "Zaza Katsitadze"


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


@pytest.mark.parametrize("ka,expected", [
    ("გიორგი ცინცაძე",   "giorgi tsintsadze"),
    ("ღოღობერიძე",       "ghoghoberidze"),
    ("ყიფიანი",          "qipiani"),
    ("ჯავახიშვილი",      "javakhishvili"),
    ("ეკატერინე ჭელიძე", "ekaterine chelidze"),
])
def test_kartuli_to_latin_handles_full_letter_inventory(ka, expected):
    assert kartuli_to_latin(ka) == expected


@pytest.mark.parametrize("input_,expected", [
    ("ციტო",            "Cito"),
    ("ავერსი ფარმაცია", "Aversi parmatsia"),
    ("ციტო-ს კლინიკა",  "Cito-s klinika"),
])
def test_brand_token_takes_precedence_over_char_translit(input_, expected):
    assert kartuli_to_latin(input_) == expected


def test_brand_override_does_not_match_substring_of_larger_word():
    assert kartuli_to_latin("ციტოლოგი") == "tsitologi"


def test_normalize_applies_brand_override_to_full_name_en():
    record = DoctorRecord(
        source="aversi",
        source_url="https://aversiclinic.ge/x",
        full_name_ka="ციტო კლინიკის ექიმი",
    )
    assert normalize(record).full_name_en == "Cito Klinikis Ekimi"
