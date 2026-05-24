"""Clinic-name normalization shared by scrapers and the normalize-clinics DB pass.

Scrapers emit raw clinic names; aggregators in particular emit doctor role/
affiliation phrases as clinic names, and the Aversi dashboard names branches
without the brand ("Central Branch"). These helpers normalize names at both
scrape time and as a one-off pass over already-persisted rows.
"""

from __future__ import annotations

import re


_BRAND_SEP = " – "

# Aggregators (vipmed) list each doctor's "Place of Work/Position", so role and
# affiliation phrases leak in as clinic names ("Cardiologist at X", "Head of the Y
# Department"). A clinic name leads with a brand or clinic-type word; a role phrase
# leads with a profession or title (optionally behind an adjective like "Clinical").
_EN_ROLE_ADJECTIVE = (
    r"clinical|medical|scientific|general|executive|technical|interventional"
    r"|senior|deputy|associate|assistant|invited|leading|practicing|certified|board"
)
_EN_ROLE_WORD = (
    r"head|chief|deputy|director|member|president|founder|co-?founder|expert|professor"
    r"|consultant|specialist|implanter|coordinator|manager|dean|academician|acad\.|author|owner"
    r"|lecturer|internist|dentist|surgeon|therapist|physician|psychiatrist|psychologist|pathologist"
    r"|reanimatolog\w*|resuscitator|anesthesiolog\w*|\w*ologist|\w*iatrician|\w*iatrist"
)
_EN_ROLE = re.compile(
    rf"^[\s\"“”']*(?:the\s+)?(?:(?:{_EN_ROLE_ADJECTIVE})\s+)*(?:{_EN_ROLE_WORD})\b",
    re.IGNORECASE,
)
_KA_ROLE = re.compile(
    r"(ექიმ|ხელმძღვანელ|დირექტორ|ასისტენტ|რეზიდენტ|ლექტორ|პროფესორ|წევრ|დეკან)"
)


def is_role_phrase(name_en: str | None, name_ka: str | None = None) -> bool:
    """True when the name is a doctor role/affiliation phrase rather than a clinic.

    A clean English name is authoritative; name_ka is only consulted when there is
    no English name, since the two can diverge (clean clinic EN, role-phrase KA).
    """
    if name_en:
        return bool(_EN_ROLE.search(name_en))
    if name_ka:
        return bool(_KA_ROLE.search(name_ka))
    return False


def strip_sublabel(title: str) -> str:
    """Drop a trailing ``| <sub-label>`` segment (e.g. ``| ლაბორატორია``)."""
    return title.split("|")[0].strip()


def brand_prefixed(title: str, brand: str, sep: str = _BRAND_SEP) -> str:
    """Prefix ``brand`` to ``title``. Idempotent and case-insensitive on the brand."""
    clean = title.strip()
    if not clean:
        return brand
    if clean.lower().startswith(brand.lower()):
        return clean
    return f"{brand}{sep}{clean}"
