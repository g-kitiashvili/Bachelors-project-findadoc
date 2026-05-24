import pytest

from pipeline.core.translit import address_to_en


class TestAddressToEn:
    @pytest.mark.parametrize("ka, en", [
        ("ლუბლიანას ქ. 15", "Lublianas St. 15"),
        ("სულხან ცინცაძის ქუჩა N24", "Sulkhan Tsintsadzis St. #24"),
        ("თამარ მეფის გამზ. N 18", "Tamar Mepis Ave. #18"),
        ("წინანდლის ქ. N 9", "Tsinandlis St. #9"),
        ("ათონელის N 18", "Atonelis #18"),
    ])
    def test_romanizes_common_addresses(self, ka, en):
        assert address_to_en(ka) == en

    def test_strips_city_prefix(self):
        assert address_to_en("ქ. თბილისი, ჩაჩავას ქ. 1").startswith("Chachavas St. 1")

    def test_translates_avenue(self):
        assert "Ave." in address_to_en("ი. ჭავჭავაძის გამზ. 33ა")

    def test_none_and_empty(self):
        assert address_to_en(None) is None
        assert address_to_en("") is None

    def test_leaves_latin_address_untouched_enough(self):
        assert address_to_en("Krtsanisi St. 12") == "Krtsanisi St. 12"
