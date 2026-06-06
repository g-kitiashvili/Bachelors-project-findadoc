"""Georgian (Kartuli) → Latin romanization for full_name_en and slug generation.

Char table follows Georgian National 2002. `_BRAND_OVERRIDES` preempts the
table at the token level for brands that have a self-chosen Latin spelling.
"""

from __future__ import annotations

import re

from pipeline.domain.record import DoctorRecord


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
    "დიაკორი":    "Diacor",
    "დიაკორ":     "Diacor",
    "ჯეო":        "Geo",
    "ვიჟენ":      "Vision",
    "ინოვა":      "Innova",
    "ოქსფორდ":    "Oxford",
}


# Source clinic names that are wrong or incomplete at the source (a brand omitted,
# a sub-clinic listed bare). Keyed by the exact Georgian source name; the value is
# the full English display name, returned verbatim ahead of romanization.
_CLINIC_NAME_OVERRIDES: dict[str, str] = {
    "ინ ვიტრო": "Innova In Vitro",
    "ჯო ენის საუნივერსიტეტო ჰოსპიტალი": "JoAnn University Hospital",
    "ჯო ენის სამედიცინო ცენტრი": "JoAnn Medical Center",
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
    "ფილიალი": "Branch",
    "ბავშვთა": "Children's",
    "ქალთა": "Women's",
    "ონკოლოგიური": "Oncology",
}

_KARTULI_WORD = re.compile(r"[ა-ჰ]+")
_GEORGIAN_CHAR = re.compile(r"[ა-ჰ]")
_NON_SLUG = re.compile(r"[^a-z0-9-]+")
_DASH_RUN = re.compile(r"-+")
# Hyphen included so "ციტო-ს" splits and the prefix can match _BRAND_OVERRIDES.
_TOKEN_SPLIT = re.compile(r"(\s+|[.,!?;:()\[\]\-])")


def english_or_none(text: str | None) -> str | None:
    """Return the trimmed text, or None if it's empty or still contains Georgian
    script. Scrapers use this for source 'English' fields that are sometimes still
    Georgian — a Georgian value routes to the romanization fallback."""
    if not text:
        return None
    trimmed = text.strip()
    if not trimmed or _GEORGIAN_CHAR.search(trimmed):
        return None
    return trimmed


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


_GENITIVE_RULES = (("ძის", "ძე"), ("ის", "ი"), ("ას", "ა"))


def _strip_genitive(token: str) -> str:
    for suffix, repl in _GENITIVE_RULES:
        if token.endswith(suffix) and len(token) > len(suffix) + 1:
            return token[: -len(suffix)] + repl
    return token


def _clinic_token_to_en(token: str) -> str:
    if token in _CLINIC_WORD_OVERRIDES:
        return _CLINIC_WORD_OVERRIDES[token]
    if token in _BRAND_OVERRIDES:
        return _BRAND_OVERRIDES[token]
    stripped = _strip_genitive(token)
    if stripped in _CLINIC_WORD_OVERRIDES:
        return _CLINIC_WORD_OVERRIDES[stripped]
    return kartuli_to_latin(stripped)


def clinic_name_to_en(name_ka: str) -> str:
    override = _CLINIC_NAME_OVERRIDES.get(name_ka.strip())
    if override is not None:
        return override
    out: list[str] = []
    for part in _TOKEN_SPLIT.split(name_ka):
        if not part:
            continue
        if _TOKEN_SPLIT.fullmatch(part):
            out.append(part)
        else:
            out.append(_clinic_token_to_en(part))
    latin = "".join(out).strip()
    return " ".join(_title_word(w) for w in latin.split()) or name_ka


_ADDRESS_TYPE_RULES = (
    (re.compile(r"\bქუჩა\b"), "St."),
    (re.compile(r"\bქ\.(?=\s|$)"), "St."),
    (re.compile(r"\bგამზირი\b"), "Ave."),
    (re.compile(r"\bგამზ\.?(?=\s|$)"), "Ave."),
    (re.compile(r"\bშესახვევი\b"), "Ln."),
    (re.compile(r"\bჩიხი\b"), "Lane"),
    (re.compile(r"\bმოედანი\b"), "Sq."),
    (re.compile(r"\bსართული\b"), "floor"),
    (re.compile(r"\bკორპუსი\b"), "bldg."),
    (re.compile(r"\bდასახლება\b"), "settlement"),
    (re.compile(r"\bმიკრორაიონი\b"), "microdistrict"),
)
_CITY_PREFIX_RE = re.compile(r"^\s*ქ\.?\s*[ა-ჰ]+\s*,\s*")
_NUM_MARKER_RE = re.compile(r"[№N]\s*(?=\d)")


def address_to_en(address: str | None) -> str | None:
    """Romanize a Georgian street address: drop the redundant "ქ. <city>," prefix,
    translate the address-type words (ქუჩა → St., გამზირი → Ave.), normalize the
    №/N number marker to #, and romanize the remaining proper nouns."""
    if not address:
        return None
    s = _CITY_PREFIX_RE.sub("", address)
    s = _NUM_MARKER_RE.sub("#", s)
    for rx, repl in _ADDRESS_TYPE_RULES:
        s = rx.sub(repl, s)
    latin = kartuli_to_latin(s)
    words = [_title_word(w) if w[:1].isalpha() else w for w in latin.split()]
    return " ".join(words).strip() or None


def normalize(record: DoctorRecord) -> DoctorRecord:
    """Fill `full_name_en` and `slug_base` if missing.

    Transliterated EN is title-cased per word (e.g., 'Giorgi Tsintsadze').
    Slug stays lowercase. Returns a new frozen record. Idempotent.
    """
    updates: dict[str, str] = {}
    # Collapse internal whitespace runs ("Zaza  Katsitadze" -> "Zaza Katsitadze");
    # str_strip_whitespace only trims the ends, not double spaces inside the name.
    name_ka = " ".join(record.full_name_ka.split())
    if name_ka != record.full_name_ka:
        updates["full_name_ka"] = name_ka
    if record.full_name_en is None:
        latin = kartuli_to_latin(name_ka).strip()
        updates["full_name_en"] = " ".join(w.capitalize() for w in latin.split())
    else:
        name_en = " ".join(record.full_name_en.split())
        if name_en != record.full_name_en:
            updates["full_name_en"] = name_en
    if record.slug_base is None:
        updates["slug_base"] = slugify(name_ka)
    if not updates:
        return record
    return record.model_copy(update=updates)
