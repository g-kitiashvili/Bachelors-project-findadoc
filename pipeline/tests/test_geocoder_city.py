from __future__ import annotations

from pipeline.services.geocoder import (
    clean_address,
    detect_city,
    drop_leading_given_name,
    fix_street_spelling,
    geocode_queries,
    street_core,
)

# longest-first, as the pass supplies them; includes the 4-char cities Poti and Gori
# (the pass must feed these in — a >=5 length floor would silently drop them).
_CITIES = [
    ("მარნეული", "Marneuli"),
    ("გურჯაანი", "Gurjaani"),
    ("ქუთაისი", "Kutaisi"),
    ("რუსთავი", "Rustavi"),
    ("ბორჯომი", "Borjomi"),
    ("თელავი", "Telavi"),
    ("ფოთი", "Poti"),
    ("გორი", "Gori"),
]


def test_detects_city_named_in_clinic_text():
    assert detect_city("Aversi – Telavi Branch", _CITIES) == ("თელავი", "Telavi")


def test_detects_four_char_city_poti():
    # ფოთი/Poti is 4 chars; it must still be detected from the branch name so a
    # city-less Poti street address geocodes to Poti, not the Tbilisi default.
    assert detect_city("ავერსი – ფოთის ფილიალი", _CITIES) == ("ფოთი", "Poti")
    assert detect_city("Aversi – Gori №1 Branch", _CITIES) == ("გორი", "Gori")


def test_detects_georgian_genitive_form():
    # "ქუთაისის" (genitive) contains "ქუთაისი"
    assert detect_city("ქუთაისის სამედიცინო ცენტრი", _CITIES) == ("ქუთაისი", "Kutaisi")


def test_defaults_to_tbilisi_when_no_city_named():
    assert detect_city("Medison Holdingi, Vazha Pshavelas #83/11", _CITIES) == ("თბილისი", "Tbilisi")


def test_ignores_city_name_buried_mid_word():
    # "Gori" is a substring of "Didgori" (a Tbilisi locality) but not at a word start,
    # so it must NOT match — otherwise a Tbilisi clinic mis-geocodes to Gori.
    assert detect_city("Evex Didgori Clinic", _CITIES) == ("თბილისი", "Tbilisi")
    assert detect_city("დიდგორის კლინიკა", _CITIES) == ("თბილისი", "Tbilisi")


def test_detects_vowel_final_city_in_genitive():
    # ახმეტა ends in a vowel, so its genitive drops it (ახმეტა -> ახმეტის); a plain prefix
    # match misses that. The branch name must still resolve to Akhmeta, not the Tbilisi default.
    cities = [("ახმეტა", "Akhmeta"), *_CITIES]
    assert detect_city("ავერსი – ახმეტის ფილიალი", cities) == ("ახმეტა", "Akhmeta")


def test_detects_city_in_locative_form():
    # "ბათუმში" (in Batumi): ბათუმი loses its final ი before -ში, so a prefix match misses.
    cities = [("ბათუმი", "Batumi"), *_CITIES]
    assert detect_city("ევექსის კლინიკა ბათუმში", cities) == ("ბათუმი", "Batumi")


def test_gorgasali_street_does_not_match_gori():
    # "გორგასლის" (a Tbilisi avenue) contains "გორ" but is not the city Gori; the word-boundary
    # anchor must keep the declension matcher from mis-detecting it.
    assert detect_city("ვახტანგ გორგასლის გამზირი 12", _CITIES) == ("თბილისი", "Tbilisi")


def test_clean_address_expands_abbreviations_and_strips_markers():
    assert clean_address("ი. ჭავჭავაძის გამზ. N33") == "ჭავჭავაძის გამზირი 33"
    assert clean_address("დ.გურამიშვილის #64") == "გურამიშვილის 64"
    assert clean_address("გუდამაყრის ქ. 4") == "გუდამაყრის ქუჩა 4"
    assert clean_address("წინანდლის № 9-3") == "წინანდლის 9-3"


def test_clean_address_leaves_full_street_type_untouched():
    # must not double-expand an already-spelled-out "გამზირი"
    assert clean_address("ვაჟა-ფშაველას გამზირი 83") == "ვაჟა-ფშაველას გამზირი 83"


def test_clean_address_expands_street_abbrev_before_number():
    # "ქ." glued to an N-number (no space) must still expand to "ქუჩა"
    assert clean_address("ლუბლიანას ქ.N18/20") == "ლუბლიანას ქუჩა 18/20"
    # the number-anchored rule must not fire when a letter follows (city marker, not street)
    assert "ქუჩა" not in clean_address("ლუბლიანას ქ.ფოთი")


def test_street_core_drops_leading_district():
    assert street_core("დიღომი, ლუბლიანას ქ. 5") == "ლუბლიანას ქუჩა 5"


def test_street_core_drops_trailing_plot_and_floor():
    assert street_core("აღმაშენებლის ხეივანი N234, ნაკვეთი 14/470") == "აღმაშენებლის ხეივანი 234"
    assert street_core("ლუბლიანას ქ. 5 მე-9 სართული") == "ლუბლიანას ქუჩა 5"


def test_street_core_plain_address_unchanged():
    assert street_core("ვაჟა-ფშაველას გამზირი 83") == "ვაჟა-ფშაველას გამზირი 83"


def test_clean_address_ungluess_abbrev_from_number():
    assert clean_address("ვაჟა-ფშაველას გამზ.29") == "ვაჟა-ფშაველას გამზირი 29"


def test_clean_address_strips_parenthetical_and_address_word():
    assert clean_address("რამიშვილის 5 (არკაში)") == "რამიშვილის 5"
    assert clean_address("მისამართი: კონსტიტუციის 7ა") == "კონსტიტუციის 7ა"


def test_street_core_strips_trailing_price():
    assert street_core("ფალიაშვილის ქ. 39  კონსულტაცია 70 ლ") == "ფალიაშვილის ქუჩა 39"


def test_street_core_splits_on_branch_separator():
    # A branch label sits before the street, joined by a pipe/bullet; isolate the street.
    assert street_core("ცენტრალური ფილიალი | ვაჟა ფშაველას 27ბ") == "ვაჟა ფშაველას 27ბ"
    assert street_core("წერეთლის #69; ალექსიძის 1") == "წერეთლის 69"


def test_street_core_strips_leading_postal_code():
    assert street_core("ისანი-სამგორის რაიონი, 0144 წინანდლის ქ. 9") == "წინანდლის ქუჩა 9"


def test_drop_leading_given_name_keeps_surname_street():
    # OSM indexes a person-named street by the surname; the given name defeats the match.
    assert drop_leading_given_name("შოთა რუსთაველის ქუჩა 68") == "რუსთაველის ქუჩა 68"
    assert drop_leading_given_name("დავით აღმაშენებლის გამზირი 10") == "აღმაშენებლის გამზირი 10"


def test_drop_leading_given_name_leaves_bare_street_untouched():
    # A bare "<surname> ქუჩა <no>" must not lose its surname.
    assert drop_leading_given_name("რუსთაველის ქუჩა 68") == "რუსთაველის ქუჩა 68"
    # No street-type word -> nothing to anchor on, leave as-is.
    assert drop_leading_given_name("ვაჟა ფშაველას 27ბ") == "ვაჟა ფშაველას 27ბ"


def test_geocode_queries_include_surname_only_variant():
    queries = geocode_queries("შოთა რუსთაველის ქუჩა №68", None, "ახმეტა", "Akhmeta")
    assert any(q == "რუსთაველის ქუჩა 68, ახმეტა" for q in queries), queries


def test_fix_street_spelling_restores_dropped_vowel():
    # The source drops a vowel that OSM keeps in the street's full genitive, so the bare
    # Georgian query misses; restore it for the known high-traffic medical streets.
    assert fix_street_spelling("წინანდლის ქუჩა 9") == "წინანდალის ქუჩა 9"
    assert fix_street_spelling("გუდამაყრის ქუჩა 4") == "გუდამაყარის ქუჩა 4"


def test_fix_street_spelling_leaves_other_addresses_untouched():
    assert fix_street_spelling("ვაჟა-ფშაველას გამზირი 83") == "ვაჟა-ფშაველას გამზირი 83"


def test_geocode_queries_are_georgian_first_then_transliterated():
    queries = geocode_queries("ვაჟა ფშაველას 27ბ", None, "თბილისი", "Tbilisi")
    assert queries[0] == "ვაჟა ფშაველას 27ბ, თბილისი"
    # Nominatim matches Latin street names more loosely, so a romanized candidate follows
    # the Georgian ones and recovers addresses whose Georgian spelling just misses.
    assert any(q == "Vazha Pshavelas 27b, Tbilisi" for q in queries), queries


def test_geocode_queries_apply_spelling_fix_to_georgian():
    queries = geocode_queries("წინანდლის ქ. 9", None, "თბილისი", "Tbilisi")
    assert queries[0] == "წინანდალის ქუჩა 9, თბილისი"
    assert not any("წინანდლის" in q for q in queries), queries


def test_geocode_queries_clean_english_address_core():
    # An English-only address with a leading city and an N marker must yield a cleaned candidate.
    queries = geocode_queries(None, "Batumi, Selim Khimshiashvili St. N 20", "ბათუმი", "Batumi")
    assert "Selim Khimshiashvili St. 20, Batumi" in queries, queries


def test_geocode_queries_dedupe_and_prefer_source_english():
    queries = geocode_queries("რუსთაველის გამზ. 1", "Rustaveli Ave 1", "თბილისი", "Tbilisi")
    assert len(queries) == len(set(queries))
    assert "Rustaveli Ave 1, Tbilisi" in queries
