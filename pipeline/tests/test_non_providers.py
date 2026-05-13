from __future__ import annotations

from pipeline.core.non_providers import NonProviderList, _Rule
from pipeline.core.taxonomy import normalize_alias


def test_substring_rule_matches_role_word_anywhere():
    npl = NonProviderList([_Rule(text=normalize_alias("ექთანი"), substring=True)])
    assert npl.matches("ჯო ენის საუნივერსიტეტო ჰოსპიტლის მთავარი ექთანი", None)


def test_exact_rule_requires_full_string():
    npl = NonProviderList([_Rule(text=normalize_alias("მეთოდისტი"), substring=False)])
    assert npl.matches("მეთოდისტი", None)
    assert not npl.matches("მეთოდისტის ასისტენტი", None)


def test_no_match_returns_false():
    npl = NonProviderList([_Rule(text=normalize_alias("ვეტერინარი"), substring=True)])
    assert not npl.matches("კარდიოლოგია", "Cardiology")
