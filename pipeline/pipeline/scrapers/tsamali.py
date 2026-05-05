"""tsamali.ge scraper — doctor-booking aggregator (multi-city), static HTTP via httpx.

The profile pages carry no reliable structured city — clinic blocks list only a
street address, and the JSON-LD addressLocality is a site-wide "Tbilisi" default.
The only authoritative per-doctor city signal is the city filter at
/doctors/city/<id>, whose select maps each city id to a Georgian city name.

discover() therefore walks the per-city listings, harvesting profile links and
recording each doctor's city as it goes; extract() reads that city back from the
discovery map keyed by profile URL.

Coverage note: only Tbilisi (city 1) paginates fully on the server side. The
smaller cities expose just their first listing page (a handful of doctors each),
so the non-Tbilisi roster captured here is a subset — the remainder is reachable
only via the flat /doctors/N listing, which carries no city. We prefer correct
per-city attribution over the larger-but-cityless flat roster.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from urllib.parse import urljoin, urlparse

import structlog
from bs4 import BeautifulSoup

from pipeline.core.record import ClinicRef, DoctorRecord
from pipeline.core.registry import register
from pipeline.core.static_scraper import StaticHtmlScraper


log = structlog.get_logger("pipeline.tsamali")

_COUNT_RE = re.compile(r"\((\d+)\)")


class TsamaliScraper(StaticHtmlScraper):
    name = "tsamali"
    _BASE = "https://tsamali.ge"
    _CITY_SELECT_ID = "submiter_mimartuleba"
    _CITY_LIST_URL = "https://tsamali.ge/doctors"
    profile_link_selector = "div.doctor_items div.doctor_item a.doctor_item_title"
    _NAME_SELECTOR = "h1"
    _SPECIALTY_SELECTOR = "a[href^='/eqimebi/']"
    _PHOTO_SELECTOR = "meta[property='og:image']"

    def __init__(self, fetcher=None) -> None:
        super().__init__(fetcher, rate_per_sec=3.0)
        self._city_by_url: dict[str, str] = {}

    def _city_map(self) -> dict[str, tuple[str, int | None]]:
        soup = BeautifulSoup(self.fetcher.get(self._CITY_LIST_URL), "lxml")
        select = soup.select_one(f"select#{self._CITY_SELECT_ID}")
        cities: dict[str, tuple[str, int | None]] = {}
        if select is None:
            return cities
        for option in select.select("option[value]"):
            city_id = option.get("value")
            label = option.get_text(strip=True)
            name = label.split("(")[0].strip()
            count_match = _COUNT_RE.search(label)
            advertised = int(count_match.group(1)) if count_match else None
            if city_id and name:
                cities[city_id] = (name, advertised)
        return cities

    def _city_listing_urls(self, city_id: str) -> Iterator[str]:
        page = 1
        while True:
            suffix = "" if page == 1 else f"/{page}"
            yield f"{self._BASE}/doctors/city/{city_id}{suffix}"
            page += 1

    def index_urls(self) -> Iterable[str]:
        for city_id in self._city_map():
            yield from self._city_listing_urls(city_id)

    def discover(self) -> Iterator[str]:
        seen: set[str] = set()
        for city_id, (city_name, advertised) in self._city_map().items():
            harvested = 0
            for listing_url in self._city_listing_urls(city_id):
                soup = BeautifulSoup(self.fetcher.get(listing_url), "lxml")
                cards = soup.select(self.profile_link_selector)
                if not cards:
                    break
                for card in cards:
                    href = card.get("href")
                    if not href:
                        continue
                    absolute = urljoin(listing_url, href)
                    self._city_by_url[absolute] = city_name
                    harvested += 1
                    if absolute in seen:
                        continue
                    seen.add(absolute)
                    yield absolute
            if advertised is not None and harvested < advertised:
                log.warning(
                    "coverage_capped",
                    city=city_name,
                    harvested=harvested,
                    advertised=advertised,
                )

    def _clinics(self, soup: BeautifulSoup, url: str) -> list[ClinicRef]:
        clinics: list[ClinicRef] = []
        seen: set[str] = set()
        for block in soup.select("div.clinic_link"):
            link = block.select_one("a[href*='/klinika/']")
            if link is None:
                continue
            href = link.get("href")
            name = link.get_text(strip=True)
            if not href or not name:
                continue
            parts = urlparse(urljoin(url, href)).path.strip("/").split("/")
            if len(parts) < 2 or parts[0] != "klinika":
                continue
            clinic_url = f"{self._BASE}/klinika/{parts[1]}"
            if clinic_url in seen:
                continue
            seen.add(clinic_url)
            addr_el = block.select_one("div.clinic_link_div2")
            address = (
                addr_el.get_text(" ", strip=True).replace("(რუკის ჩვენება)", "").strip() or None
                if addr_el is not None
                else None
            )
            clinics.append(ClinicRef(source_url=clinic_url, name_ka=name, address=address))
        return clinics

    def parse(self, soup: BeautifulSoup, url: str) -> DoctorRecord | None:
        if not urlparse(url).path.startswith("/eqimi/"):
            return None
        name_el = soup.select_one(self._NAME_SELECTOR)
        if name_el is None or not name_el.get_text(strip=True):
            return None
        specialty_el = soup.select_one(self._SPECIALTY_SELECTOR)
        photo_el = soup.select_one(self._PHOTO_SELECTOR)
        photo_url = photo_el.get("content") if photo_el else None
        return DoctorRecord(
            source=self.name,
            source_url=url,
            full_name_ka=name_el.get_text(strip=True),
            specialty_ka=specialty_el.get_text(strip=True) if specialty_el else None,
            photo_url=urljoin(url, photo_url) if photo_url else None,
            city=self._city_by_url.get(url),  # populated by discover() before this url is yielded
            clinics=self._clinics(soup, url),
        )


register(TsamaliScraper())
