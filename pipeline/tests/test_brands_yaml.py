from __future__ import annotations

from pathlib import Path

from pipeline.domain.taxonomy import load_brands

_BRANDS = Path(__file__).resolve().parent.parent / "pipeline" / "data" / "brands.yaml"


def test_registry_has_unique_slugs_and_required_fields():
    rows = load_brands(_BRANDS)
    assert len(rows) == 13
    slugs = [r["slug"] for r in rows]
    assert len(slugs) == len(set(slugs))
    for r in rows:
        assert r["name_en"] and r["name_ka"]
        assert r["match_ka"] and all(p.strip() for p in r["match_ka"])


def test_no_match_prefix_is_a_prefix_of_another_brands():
    # Guards the false-merge traps: e.g. 'ნიუ ჰოსპიტალს' must not be a prefix of
    # 'ნიუ ვიჟენ' (and vice versa), or a clinic could match two brands.
    rows = load_brands(_BRANDS)
    prefixes = [(r["slug"], p) for r in rows for p in r["match_ka"]]
    for slug_a, pa in prefixes:
        for slug_b, pb in prefixes:
            if slug_a != slug_b:
                assert not pa.startswith(pb), f"{slug_a} prefix {pa!r} collides with {slug_b} {pb!r}"
