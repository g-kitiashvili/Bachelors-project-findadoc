from __future__ import annotations

import pytest

from pipeline.core.taxonomy import build_alias_index, normalize_alias


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
