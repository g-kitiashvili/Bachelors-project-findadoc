"""Geocode clinic addresses to coordinates via OpenStreetMap Nominatim.

Nominatim is free and key-less but asks for <=1 req/sec; HttpxFetcher's rate limiter
enforces that.

Clinic source addresses usually omit the city, and many Georgian street names collide
with rural village names (e.g. Tsinandali, Patardzeuli are both Tbilisi streets and
Kakheti villages), so a bare "<street>, Georgia" query resolves to the wrong town. We
therefore append a city to every query: a known city named in the clinic's name/address
when one is present (e.g. "Aversi – Telavi Branch" -> Telavi), else Tbilisi, where the
overwhelming majority of clinics are. countrycodes=ge keeps results inside Georgia.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from urllib.parse import urlencode

import psycopg
import structlog

from pipeline.core.fetcher import FetchError, HttpxFetcher

log = structlog.get_logger("pipeline.geocoder")

_NOMINATIM = "https://nominatim.openstreetmap.org/search"
_DEFAULT_CITY = ("თბილისი", "Tbilisi")


class Geocoder:
    def __init__(self, fetcher=None) -> None:
        self.fetcher = fetcher or HttpxFetcher(rate_per_sec=1.0)

    def geocode(self, query: str) -> tuple[float, float] | None:
        """Return (lat, lng) for a free-text place query, or None if unresolved.

        countrycodes=ge restricts results to the country of Georgia so a query like
        "..., Georgia" can't match the US state of Georgia."""
        url = f"{_NOMINATIM}?{urlencode({'q': query, 'format': 'json', 'limit': 1, 'countrycodes': 'ge'})}"
        try:
            payload = json.loads(self.fetcher.get(url))
        except (FetchError, json.JSONDecodeError):
            return None
        if not isinstance(payload, list) or not payload:
            return None
        try:
            return float(payload[0]["lat"]), float(payload[0]["lon"])
        except (KeyError, ValueError, TypeError):
            return None


# Source addresses use abbreviations, initials and #/№/N markers that Nominatim fails
# on ("ი. ჭავჭავაძის გამზ. #33" -> no match, but "ჭავჭავაძის გამზირი 33" resolves).
_PARENTHETICAL = re.compile(r"\([^)]*\)")
_LEADING_ADDRESS_WORD = re.compile(r"^\s*მისამართ\S*[:\s]+")
_LEADING_INITIAL = re.compile(r"^\s*[ა-ჰ]\.\s*")
_ABBREV_RULES = (
    (re.compile(r"\bგამზ\."), "გამზირი"),
    (re.compile(r"\bგზატკ\."), "გზატკეცილი"),
    (re.compile(r"\bქ\.(?=\s|$)"), "ქუჩა"),
    (re.compile(r"\bქ\.(?=N?\d)"), "ქუჩა "),  # "ლუბლიანას ქ.N18" -> "ლუბლიანას ქუჩა 18"
    (re.compile(r"\bჩიხ\."), "ჩიხი"),
    (re.compile(r"\bგამზირ\.(?=\s|$)"), "გამზირი"),
)
_GLUED_NUM = re.compile(r"(?<=[ა-ჰ])(?=\d)")  # "გამზირი29" -> "გამზირი 29"

# Street-type words and trailing unit/plot/floor/price noise. Nominatim resolves a bare
# "<street> <number>, <city>" but fails when the query also carries a leading district
# ("დიღომი, ...") or a trailing plot/floor/price ("..., ნაკვეთი 14/470", "... კონსულტაცია 70 ლ").
_STREET_TYPES = ("ქუჩა", "ქ.", "გამზირი", "გამზ", "ხეივანი", "ჩიხ", "გზატკ", "შესახვევი")
_UNIT_NOISE = re.compile(
    r"\s*(ნაკვეთ|სართულ|მე-?\d+\s*სართ|ბინა|კორპუს|შენობა|პოდიეზდ|კონსულტაცი|ფასი)\S*.*$"
)
_NUM_MARKER = re.compile(r"[#№N]\s*(?=\d)")


def clean_address(address: str) -> str:
    """Normalize a Georgian street address into a geocodable form: strip parentheticals
    and a leading "address:" word/person-initial, expand street-type abbreviations, drop
    the #/№/N marker, and unglue a street name run into its number."""
    a = _PARENTHETICAL.sub(" ", address)
    a = _LEADING_ADDRESS_WORD.sub("", a.strip())
    a = _LEADING_INITIAL.sub("", a.strip())
    for pat, repl in _ABBREV_RULES:
        a = pat.sub(repl, a)
    a = _NUM_MARKER.sub("", a)
    a = _GLUED_NUM.sub(" ", a)
    return " ".join(a.split())


def street_core(address: str) -> str:
    """Isolate the geocodable "<street> <number>" core from a messy address.

    Picks the comma-segment that names a street (else the first with a digit), drops a
    leading district and trailing plot/floor noise, and cleans it. "დიღომი, ლუბლიანას ქ. 5"
    -> "ლუბლიანას ქუჩა 5"; "აღმაშენებლის ხეივანი N234, ნაკვეთი 14/470" -> "აღმაშენებლის ხეივანი 234"."""
    segments = [s.strip() for s in address.split(",") if s.strip()]
    if not segments:
        return clean_address(address)
    chosen = next((s for s in segments if any(t in s for t in _STREET_TYPES)), None)
    if chosen is None:
        chosen = next((s for s in segments if re.search(r"\d", s)), segments[0])
    return clean_address(_UNIT_NOISE.sub("", chosen))


def _names_a_city(name: str, blob: str) -> bool:
    """True if `name` appears in `blob` at a word start (not mid-word).

    Word-start (not bare substring) matching keeps Georgian genitive forms working —
    the city name is a prefix of the inflected word, so trailing letters are fine
    ("ფოთის" still matches "ფოთი") — while rejecting mid-word collisions where a short
    city name is buried inside an unrelated word ("Gori" inside "Didgori", "Ingoroqva")."""
    if not name:
        return False
    return re.search(rf"(?<!\w){re.escape(name)}", blob) is not None


def detect_city(blob: str, cities: list[tuple[str, str]]) -> tuple[str, str]:
    """Return the (name_ka, name_en) of the first known city found in `blob`, else Tbilisi.

    `cities` must be sorted longest-first so a specific name wins over a shorter one that
    is a prefix of it. Matching is word-start anchored (see `_names_a_city`) so genitive
    forms still match but mid-word substrings (e.g. "Gori" in "Didgori") do not."""
    low = blob.lower()
    for name_ka, name_en in cities:
        if _names_a_city((name_ka or "").lower(), low) or _names_a_city((name_en or "").lower(), low):
            return name_ka, name_en
    return _DEFAULT_CITY


@dataclass(frozen=True)
class GeocodeStats:
    total: int
    geocoded: int
    failed: int


class GeocodeClinicsPass:
    def __init__(self, dsn: str, *, geocoder: Geocoder | None = None) -> None:
        self._dsn = dsn
        self._geocoder = geocoder or Geocoder()

    def run(self, limit: int | None = None, *, overwrite: bool = False) -> GeocodeStats:
        """Geocode clinics. By default only fills clinics with no location yet; pass
        overwrite=True to re-geocode every active clinic (used to correct bad placements)."""
        with psycopg.connect(self._dsn, autocommit=True) as conn, conn.cursor() as cur:
            # Known Georgian city/region names (>=4 chars to avoid short-substring false
            # matches), longest first so the most specific name wins. The 4-char floor is
            # deliberate: the shortest real city names are ფოთი (Poti) and გორი (Gori), so
            # a >=5 floor silently drops them and their branches mis-geocode to Tbilisi.
            cur.execute(
                "SELECT name_ka, name_en FROM location WHERE char_length(name_ka) >= 4 "
                "ORDER BY char_length(name_ka) DESC",
            )
            cities = [(r[0], r[1]) for r in cur.fetchall()]
            where = "status='ACTIVE'" if overwrite else "status='ACTIVE' AND location IS NULL"
            sql = f"SELECT id, name_ka, name_en, address, address_en FROM clinic WHERE {where} ORDER BY id"
            if limit is not None:
                sql += f" LIMIT {int(limit)}"
            cur.execute(sql)
            rows = cur.fetchall()
            geocoded = failed = 0
            for cid, name_ka, name_en, address, address_en in rows:
                blob = " ".join(t for t in (name_ka, name_en, address, address_en) if t)
                city_ka, city_en = detect_city(blob, cities)
                coords = None
                if address:
                    # ordered KA candidates: cleaned full, raw, then the street-only core
                    # (strips leading district / trailing plot+floor that Nominatim chokes on)
                    seen_q: set[str] = set()
                    for q in (clean_address(address), address, street_core(address)):
                        if not q or q in seen_q:
                            continue
                        seen_q.add(q)
                        coords = self._geocoder.geocode(f"{q}, {city_ka}")
                        if coords is not None:
                            break
                if coords is None and address_en:
                    coords = self._geocoder.geocode(f"{address_en}, {city_en}")
                # No precise street-level match -> leave location NULL. We deliberately do
                # NOT fall back to the city centroid: that collapsed every unresolved
                # Tbilisi clinic onto one point (Freedom Square), littering the map with
                # false pins. A clinic with no precise coordinate is simply absent from the
                # map; it stays findable via its city/region filter, which uses location_id.
                if coords is None:
                    failed += 1
                    continue
                lat, lng = coords
                cur.execute(
                    "UPDATE clinic SET location = ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography WHERE id = %s",
                    (lng, lat, cid),
                )
                geocoded += 1
            stats = GeocodeStats(len(rows), geocoded, failed)
            log.info("geocode_complete", overwrite=overwrite, **stats.__dict__)
            return stats
