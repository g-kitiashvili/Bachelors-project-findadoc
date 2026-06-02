from __future__ import annotations

from pipeline.core.geocoder import clean_address, detect_city, street_core

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
