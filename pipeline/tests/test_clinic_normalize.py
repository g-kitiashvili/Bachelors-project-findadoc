import pytest

from pipeline.domain.clinic_normalize import brand_prefixed, is_role_phrase, strip_sublabel


class TestStripSublabel:
    def test_drops_pipe_sublabel(self):
        assert strip_sublabel("ცენტრალური ფილიალი | ლაბორატორია") == "ცენტრალური ფილიალი"

    def test_leaves_plain_title_untouched(self):
        assert strip_sublabel("ცენტრალური ფილიალი") == "ცენტრალური ფილიალი"

    def test_trims_whitespace(self):
        assert strip_sublabel("  Central Branch  ") == "Central Branch"

    def test_empty_string(self):
        assert strip_sublabel("") == ""


class TestBrandPrefixed:
    def test_prefixes_georgian_brand(self):
        assert brand_prefixed("ცენტრალური ფილიალი", "ავერსი") == "ავერსი – ცენტრალური ფილიალი"

    def test_prefixes_latin_brand(self):
        assert brand_prefixed("Central Branch", "Aversi") == "Aversi – Central Branch"

    def test_idempotent_when_already_prefixed(self):
        once = brand_prefixed("Central Branch", "Aversi")
        assert brand_prefixed(once, "Aversi") == once

    def test_idempotent_is_case_insensitive(self):
        assert brand_prefixed("aversi clinic", "Aversi") == "aversi clinic"

    def test_empty_title_returns_brand_only(self):
        assert brand_prefixed("", "Aversi") == "Aversi"


class TestIsRolePhrase:
    @pytest.mark.parametrize("name_en", [
        "Cardiologist at the Acad. G. Chapidze Emergency Cardiology Center",
        "Head of the Ophthalmology Department",
        "Clinical Director of the Institute of Clinical Oncology",
        "Medical Director",
        "Deputy Director of Bokhua Memorial Cardiovascular Center",
        "Member of the Georgian Association of Urologists",
        "President of the Georgian Association of Women Doctors",
        "Founder of the Institute of Clinical Oncology",
        "Implanter of PRP gums plasmotherapy in Georgia",
        "Internist",
        "Oncologist of the Central Branch of Aversi Clinic",
        "Anesthesiologist-resuscitator of West Georgia Medical Center",
        "Invited Lecturer",
        "Author of 40 scientific papers",
    ])
    def test_flags_role_phrases(self, name_en):
        assert is_role_phrase(name_en) is True

    @pytest.mark.parametrize("name_en", [
        "Aversi Clinic",
        "American Hospital Tbilisi",
        "Caucasus Medical Center",
        "“Kanveni” National Center of Dermatology and Venerology",
        "GGRC Georgian-German Reproductive Center",
        "Medical Diagnostic Center “Cito”",
        "Jerarsi Clinic",
        "I. Tsitsishvili Pediatric Clinic",
        "National Center of Otorhinolaryngology",
        "German Hospital",
        "Prof. Zhordania and Prof. Khomasuridze Institute of Reproductology",
        "Todua Clinic",
    ])
    def test_keeps_clinic_names(self, name_en):
        assert is_role_phrase(name_en) is False

    def test_detects_georgian_role_when_no_english(self):
        assert is_role_phrase(None, "ავერსის კლინიკის ექიმი-ნევროლოგი") is True

    def test_keeps_georgian_clinic_name(self):
        assert is_role_phrase(None, "ავერსის კლინიკა") is False
