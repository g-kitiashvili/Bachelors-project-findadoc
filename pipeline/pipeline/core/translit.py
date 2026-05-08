"""Georgian (Kartuli) → Latin romanization for full_name_en and slug generation.

Char table follows Georgian National 2002. `_BRAND_OVERRIDES` preempts the
table at the token level for brands that have a self-chosen Latin spelling.
"""

from __future__ import annotations

import re

from pipeline.core.record import DoctorRecord


_KARTULI_TO_LATIN: dict[str, str] = {
    "ა": "a",  "ბ": "b",  "გ": "g",  "დ": "d",  "ე": "e",
    "ვ": "v",  "ზ": "z",  "თ": "t",  "ი": "i",  "კ": "k",
    "ლ": "l",  "მ": "m",  "ნ": "n",  "ო": "o",  "პ": "p",
    "ჟ": "zh", "რ": "r",  "ს": "s",  "ტ": "t",  "უ": "u",
    "ფ": "p",  "ქ": "k",  "ღ": "gh", "ყ": "q",  "შ": "sh",
    "ჩ": "ch", "ც": "ts", "ძ": "dz", "წ": "ts", "ჭ": "ch",
    "ხ": "kh", "ჯ": "j",  "ჰ": "h",
}


_BRAND_OVERRIDES: dict[str, str] = {
    "ციტო":      "Cito",
    "ავერსი":    "Aversi",
    "ავერსის":   "Aversi",
    "ევექსი":    "Evex",
    "ევექსის":   "Evex",
    "მედკლუბი":  "MedClub",
    "მედალფა":   "Medalpha",
    "ჰელსიკორი": "Helsicore",
    "ნიუ":        "New",
    "ჰოსპიტალსი": "Hospitals",
    "ვივო":       "Vivo",
    "მედიქალ":    "Medical",
}


# Common Georgian clinic words are translated (not transliterated) so EN names
# read naturally; proper nouns fall through to romanization. "სახელობის"
# ("named after") is dropped for readable English word order.
_CLINIC_WORD_OVERRIDES: dict[str, str] = {
    "სამედიცინო": "Medical",
    "ცენტრი": "Center",
    "ცენტრალური": "Central",
    "კლინიკა": "Clinic",
    "კლინიკური": "Clinical",
    "საავადმყოფო": "Hospital",
    "ჰოსპიტალი": "Hospital",
    "პოლიკლინიკა": "Polyclinic",
    "სახელობის": "",
    "კარდიოვასკულარული": "Cardiovascular",
    "რეპროდუქციული": "Reproductive",
    "ეკოსისტემა": "Ecosystem",
    "სამკურნალო": "Treatment",
    "საკონსულტაციო": "Consultation",
    "კაბინეტი": "Office",
    "ჯანმრთელობის": "Health",
    "სექსუალური": "Sexual",
    "საუნივერსიტეტო": "University",
    "რესპუბლიკური": "Republican",
    "ეროვნული": "National",
    "უროლოგიის": "Urology",
    "დიაგნოსტიკური": "Diagnostic",
    "სტომატოლოგიური": "Dental",
    "სტომატოლოგია": "Dentistry",
    "სამშობიარო": "Maternity",
    "ინსტიტუტი": "Institute",
    "და": "and",
    "ქირურგია": "Surgery",
    "ქირურგიის": "Surgery",
    "ექსპერიმენტული": "Experimental",
    "რეპროდუქტოლოგია": "Reproductive",
    "რეპროდუქტოლოგიის": "Reproductive",
    "ლაბორატორია": "Laboratory",
    "ლაბორატორიული": "Laboratory",
    "ბავშვთა": "Children's",
    "ქალთა": "Women's",
    "ონკოლოგიური": "Oncology",
}

_KARTULI_WORD = re.compile(r"[ა-ჰ]+")
_NON_SLUG = re.compile(r"[^a-z0-9-]+")
_DASH_RUN = re.compile(r"-+")
# Hyphen included so "ციტო-ს" splits and the prefix can match _BRAND_OVERRIDES.
_TOKEN_SPLIT = re.compile(r"(\s+|[.,!?;:()\[\]\-])")


def _token_to_latin(token: str) -> str:
    if token in _BRAND_OVERRIDES:
        return _BRAND_OVERRIDES[token]
    return "".join(_KARTULI_TO_LATIN.get(ch, ch) for ch in token)


def kartuli_to_latin(s: str) -> str:
    if not s:
        return ""
    parts = _TOKEN_SPLIT.split(s)
    out: list[str] = []
    for part in parts:
        if not part:
            continue
        if _TOKEN_SPLIT.fullmatch(part):
            out.append(part)
        else:
            out.append(_token_to_latin(part))
    return "".join(out)


def slugify(name: str) -> str:
    """Lowercase Latin slug from a (possibly Georgian) display name."""
    latin = kartuli_to_latin(name).lower()
    no_punct = _NON_SLUG.sub("-", latin)
    collapsed = _DASH_RUN.sub("-", no_punct)
    return collapsed.strip("-")


def next_slug_candidate(base: str, attempt: int) -> str:
    """Return `base` on attempt 1, `base-2` on attempt 2, ..., up to `base-99`."""
    if attempt < 1 or attempt > 99:
        raise ValueError(f"attempt must be in [1, 99], got {attempt}")
    if attempt == 1:
        return base
    return f"{base}-{attempt}"


def _title_word(word: str) -> str:
    for i, ch in enumerate(word):
        if ch.isalpha():
            return word[:i] + ch.upper() + word[i + 1 :]
    return word


def clinic_name_to_en(name_ka: str) -> str:
    translated = _KARTULI_WORD.sub(lambda m: _CLINIC_WORD_OVERRIDES.get(m.group(0), m.group(0)), name_ka)
    latin = kartuli_to_latin(translated).strip()
    return " ".join(_title_word(w) for w in latin.split()) or name_ka


def normalize(record: DoctorRecord) -> DoctorRecord:
    """Fill `full_name_en` and `slug_base` if missing.

    Transliterated EN is title-cased per word (e.g., 'Giorgi Tsintsadze').
    Slug stays lowercase. Returns a new frozen record. Idempotent.
    """
    updates: dict[str, str] = {}
    if record.full_name_en is None:
        latin = kartuli_to_latin(record.full_name_ka).strip()
        updates["full_name_en"] = " ".join(w.capitalize() for w in latin.split())
    if record.slug_base is None:
        updates["slug_base"] = slugify(record.full_name_ka)
    if not updates:
        return record
    return record.model_copy(update=updates)
