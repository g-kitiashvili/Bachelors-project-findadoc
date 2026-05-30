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
_LEADING_INITIAL = re.compile(r"^\s*[ა-ჰ]\.\s*")
_ABBREV_RULES = (
    (re.compile(r"\bგამზ\."), "გამზირი"),
    (re.compile(r"\bქ\.(?=\s|$)"), "ქუჩა"),
    (re.compile(r"\bჩიხ\."), "ჩიხი"),
    (re.compile(r"\bგამზირ\.(?=\s|$)"), "გამზირი"),
)
_NUM_MARKER = re.compile(r"[#№N]\s*(?=\d)")


def clean_address(address: str) -> str:
    """Normalize a Georgian street address into a geocodable form: drop a leading
    person-initial, expand street-type abbreviations, and strip the #/№/N marker."""
    a = _LEADING_INITIAL.sub("", address.strip())
    for pat, repl in _ABBREV_RULES:
        a = pat.sub(repl, a)
    a = _NUM_MARKER.sub("", a)
    return " ".join(a.split())


def detect_city(blob: str, cities: list[tuple[str, str]]) -> tuple[str, str]:
    """Return the (name_ka, name_en) of the first known city found in `blob`, else Tbilisi.

    `cities` must be sorted longest-first so a specific name wins over a shorter one that
    is a substring of it. Substring (not token) matching is intentional so Georgian
    genitive forms still match (e.g. "თელავის" contains "თელავი")."""
    low = blob.lower()
    for name_ka, name_en in cities:
        if (name_ka and name_ka.lower() in low) or (name_en and name_en.lower() in low):
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
            # Known Georgian city/region names (>=5 chars to avoid short-substring false
            # matches), longest first so the most specific name wins.
            cur.execute(
                "SELECT name_ka, name_en FROM location WHERE char_length(name_ka) >= 5 "
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
                    coords = self._geocoder.geocode(f"{clean_address(address)}, {city_ka}")
                    if coords is None:
                        coords = self._geocoder.geocode(f"{address}, {city_ka}")
                if coords is None and address_en:
                    coords = self._geocoder.geocode(f"{address_en}, {city_en}")
                # Last resort: the city centroid, so a clinic lands in the right city
                # (approximate spot) rather than at a stale, wrong-town coordinate.
                if coords is None:
                    coords = self._geocoder.geocode(city_ka)
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
