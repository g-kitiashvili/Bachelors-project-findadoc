from __future__ import annotations

import psycopg
import pytest

from pipeline.core.geocoder import GeocodeClinicsPass, Geocoder


class _FakeFetcher:
    def __init__(self, response: str) -> None:
        self._response = response
        self.calls: list[str] = []

    def get(self, url: str) -> str:
        self.calls.append(url)
        return self._response


def test_geocode_parses_lat_lng():
    g = Geocoder(fetcher=_FakeFetcher('[{"lat":"41.715","lon":"44.827"}]'))
    assert g.geocode("Rustaveli Ave, Georgia") == (41.715, 44.827)


def test_geocode_none_on_empty_result():
    assert Geocoder(fetcher=_FakeFetcher("[]")).geocode("nowhere") is None


def test_geocode_none_on_bad_json():
    assert Geocoder(fetcher=_FakeFetcher("<html>blocked</html>")).geocode("x") is None


class _FakeGeocoder:
    def geocode(self, query: str):
        return (41.7, 44.8)


class _RecordingGeocoder:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def geocode(self, query: str):
        self.queries.append(query)
        return (42.15, 41.67)  # Poti-ish coordinates


@pytest.mark.slow
def test_pass_sets_location_only_for_ungeocoded(postgres_container):
    with psycopg.connect(postgres_container, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE clinic RESTART IDENTITY CASCADE")
        cur.execute(
            "INSERT INTO clinic (slug, name_ka, name_en, address, last_source_url, last_updated_at, status) "
            "VALUES ('c1','კ','C1',' რუსთაველის გამზ. 1','https://x/1', now(),'ACTIVE')"
        )
    stats = GeocodeClinicsPass(postgres_container, geocoder=_FakeGeocoder()).run()
    assert stats.geocoded == 1
    with psycopg.connect(postgres_container) as conn, conn.cursor() as cur:
        cur.execute("SELECT ST_Y(location::geometry), ST_X(location::geometry) FROM clinic WHERE slug='c1'")
        lat, lng = cur.fetchone()
    assert round(lat, 1) == 41.7 and round(lng, 1) == 44.8


@pytest.mark.slow
def test_pass_qualifies_four_char_city_branch_with_its_city(postgres_container):
    """An Aversi Poti branch (city-less street address) must be geocoded with the
    Poti qualifier, not the Tbilisi default — Poti is a 4-char city name that the
    pass's city list must include."""
    with psycopg.connect(postgres_container, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE clinic RESTART IDENTITY CASCADE")
        cur.execute(
            "INSERT INTO location (slug, name_ka, name_en, sort_order) "
            "VALUES ('poti','ფოთი','Poti',30) ON CONFLICT (slug) DO NOTHING"
        )
        cur.execute(
            "INSERT INTO clinic (slug, name_ka, name_en, address, last_source_url, last_updated_at, status) "
            "VALUES ('ap','ავერსი – ფოთის ფილიალი','Aversi – Poti Branch',"
            "'დ. აღმაშენებლის ქ. #10','https://x/poti', now(),'ACTIVE')"
        )
    rec = _RecordingGeocoder()
    GeocodeClinicsPass(postgres_container, geocoder=rec).run()
    assert rec.queries, "geocoder was never called"
    assert any("ფოთი" in q for q in rec.queries), rec.queries
    assert not any("თბილისი" in q for q in rec.queries), rec.queries
