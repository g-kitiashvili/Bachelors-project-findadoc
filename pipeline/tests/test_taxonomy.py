from __future__ import annotations

import pytest

from pipeline.core.taxonomy import build_alias_index, detect_lang, load_search_keywords, normalize_alias


def test_normalize_alias_lowercases_and_collapses_whitespace():
    assert normalize_alias("  Family   Doctor ") == "family doctor"


def test_build_alias_index_includes_names_and_aliases():
    rows = [
        {
            "slug": "family-medicine",
            "name_ka": "საოჯახო მედიცინა",
            "name_en": "Family Medicine",
            "aliases": ["ოჯახის ექიმი"],
        }
    ]
    idx = build_alias_index(rows)
    assert idx[normalize_alias("ოჯახის ექიმი")] == "family-medicine"
    assert idx[normalize_alias("Family Medicine")] == "family-medicine"
    assert idx[normalize_alias("საოჯახო მედიცინა")] == "family-medicine"


def test_build_alias_index_rejects_conflicting_alias():
    rows = [
        {"slug": "a", "name_ka": "ა", "name_en": "A", "aliases": ["dup"]},
        {"slug": "b", "name_ka": "ბ", "name_en": "B", "aliases": ["dup"]},
    ]
    with pytest.raises(ValueError):
        build_alias_index(rows)


def test_detect_lang_distinguishes_georgian_from_latin():
    assert detect_lang("გული") == "ka"
    assert detect_lang("heart") == "en"
    assert detect_lang("women's health") == "en"


def test_load_search_keywords_reads_term_pairs(tmp_path):
    p = tmp_path / "search_keywords.yaml"
    p.write_text(
        "- term_en: heart\n  term_ka: გული\n  specialty: cardiology\n",
        encoding="utf-8",
    )
    rows = load_search_keywords(p)
    assert rows == [{"term_en": "heart", "term_ka": "გული", "specialty": "cardiology"}]


def test_load_search_keywords_missing_file_is_empty(tmp_path):
    assert load_search_keywords(tmp_path / "nope.yaml") == []
