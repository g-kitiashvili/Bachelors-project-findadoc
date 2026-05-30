from __future__ import annotations

from pipeline.core.geocoder import clean_address, detect_city

# longest-first, as the pass supplies them
_CITIES = [
    ("მარნეული", "Marneuli"),
    ("გურჯაანი", "Gurjaani"),
    ("ქუთაისი", "Kutaisi"),
    ("რუსთავი", "Rustavi"),
    ("ბორჯომი", "Borjomi"),
    ("თელავი", "Telavi"),
]


def test_detects_city_named_in_clinic_text():
    assert detect_city("Aversi – Telavi Branch", _CITIES) == ("თელავი", "Telavi")


def test_detects_georgian_genitive_form():
    # "ქუთაისის" (genitive) contains "ქუთაისი"
    assert detect_city("ქუთაისის სამედიცინო ცენტრი", _CITIES) == ("ქუთაისი", "Kutaisi")


def test_defaults_to_tbilisi_when_no_city_named():
    assert detect_city("Medison Holdingi, Vazha Pshavelas #83/11", _CITIES) == ("თბილისი", "Tbilisi")


def test_clean_address_expands_abbreviations_and_strips_markers():
    assert clean_address("ი. ჭავჭავაძის გამზ. N33") == "ჭავჭავაძის გამზირი 33"
    assert clean_address("დ.გურამიშვილის #64") == "გურამიშვილის 64"
    assert clean_address("გუდამაყრის ქ. 4") == "გუდამაყრის ქუჩა 4"
    assert clean_address("წინანდლის № 9-3") == "წინანდლის 9-3"


def test_clean_address_leaves_full_street_type_untouched():
    # must not double-expand an already-spelled-out "გამზირი"
    assert clean_address("ვაჟა-ფშაველას გამზირი 83") == "ვაჟა-ფშაველას გამზირი 83"
