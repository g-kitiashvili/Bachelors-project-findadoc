from __future__ import annotations

from pipeline.core.deduplicator import _clinic_key


def test_qualifier_prefix_keys_same_as_bare_name():
    assert _clinic_key("Medical Center Vivamedi") == _clinic_key("Vivamedi")
    assert _clinic_key("სამედიცინო ცენტრი ვივამედი") == _clinic_key("ვივამედი")


def test_quotes_and_case_are_ignored():
    assert _clinic_key('„ვივამედი"') == _clinic_key("ვივამედი")
    assert _clinic_key("AVERSI") == _clinic_key("aversi")


def test_distinct_core_names_stay_distinct():
    assert _clinic_key("Medical Center Vivamedi") != _clinic_key("Medical Center Aversi")


def test_name_made_only_of_qualifiers_falls_back():
    # must not collapse to empty (which would merge all bare "Medical Center" rows)
    assert _clinic_key("Medical Center") == "medical center"
    assert _clinic_key("სამედიცინო ცენტრი") == "სამედიცინო ცენტრი"
