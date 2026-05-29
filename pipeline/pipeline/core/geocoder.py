"""Geocode clinic addresses to coordinates via OpenStreetMap Nominatim.

Nominatim is free and key-less but asks for <=1 req/sec; HttpxFetcher's rate limiter
enforces that. Only clinics that have an address but no location yet are geocoded, so
re-runs are cheap and the partial coverage accumulates.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.parse import urlencode

import psycopg
import structlog

from pipeline.core.fetcher import FetchError, HttpxFetcher

log = structlog.get_logger("pipeline.geocoder")

_NOMINATIM = "https://nominatim.openstreetmap.org/search"


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


@dataclass(frozen=True)
class GeocodeStats:
    total: int
    geocoded: int
    failed: int


class GeocodeClinicsPass:
    def __init__(self, dsn: str, *, geocoder: Geocoder | None = None) -> None:
        self._dsn = dsn
        self._geocoder = geocoder or Geocoder()

    def run(self, limit: int | None = None) -> GeocodeStats:
        with psycopg.connect(self._dsn, autocommit=True) as conn, conn.cursor() as cur:
            sql = (
                "SELECT id, address, address_en, name_en FROM clinic "
                "WHERE status='ACTIVE' AND location IS NULL "
                "ORDER BY id"
            )
            if limit is not None:
                sql += f" LIMIT {int(limit)}"
            cur.execute(sql)
            rows = cur.fetchall()
            geocoded = failed = 0
            for cid, address, address_en, name_en in rows:
                # Try the street address first; fall back to the clinic name as a place
                # query (e.g. "Evex Clinic in Batumi") for branches with no usable address.
                coords = None
                if address:
                    coords = self._geocoder.geocode(f"{address}, Georgia")
                if coords is None and address_en:
                    coords = self._geocoder.geocode(f"{address_en}, Georgia")
                if coords is None and name_en:
                    coords = self._geocoder.geocode(f"{name_en}, Georgia")
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
            log.info("geocode_complete", **stats.__dict__)
            return stats
