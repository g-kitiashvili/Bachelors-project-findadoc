"""cmchospital.ge scraper — Caucasus Medical Centre (Tbilisi hospital), static SSR HTML via httpx."""

from __future__ import annotations

import re
from collections.abc import Iterator
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from pipeline.core.fetcher import FetchError
from pipeline.core.record import ClinicRef, DoctorRecord
from pipeline.core.registry import register
from pipeline.core.static_scraper import StaticHtmlScraper
from pipeline.core.translit import english_or_none

_HOSPITAL_CLINIC = ClinicRef(
    source_url="https://cmchospital.ge",
    name_ka="კავკასიის მედიცინის ცენტრი",
    name_en="Caucasus Medical Centre",
)

_PROFILE_HREF = re.compile(r"^/ge/doctors/\d+-")


class CmcScraper(StaticHtmlScraper):
    name = "cmc"
    profile_link_selector = 'a[href^="/ge/doctors/"]'
    _INDEX_URL = "https://cmchospital.ge/ge/doctors"
    _NAME_SELECTOR = "h1.display-medium"

    def __init__(self, fetcher=None) -> None:
        super().__init__(fetcher, rate_per_sec=2.0)

    def index_urls(self) -> Iterator[str]:
        page = 1
        while True:
            yield f"{self._INDEX_URL}?page={page}"
            page += 1

    def discover(self) -> Iterator[str]:
        seen: set[str] = set()
        for index_url in self.index_urls():
            soup = BeautifulSoup(self.fetcher.get(index_url), "lxml")
            new_on_page = 0
            for a in soup.select(self.profile_link_selector):
                href = a.get("href")
                if not href or not _PROFILE_HREF.match(href):
                    continue
                absolute = urljoin(index_url, href)
                if absolute in seen:
                    continue
                seen.add(absolute)
                new_on_page += 1
                yield absolute
            if new_on_page == 0:
                break

    def _en_url(self, ka_url: str) -> str | None:
        if "/ge/" not in ka_url:
            return None
        return ka_url.replace("/ge/", "/en/", 1)

    def _fetch_english_name(self, ka_url: str) -> str | None:
        en_url = self._en_url(ka_url)
        if en_url is None:
            return None
        try:
            html = self.fetcher.get(en_url)
        except FetchError:
            return None
        soup = BeautifulSoup(html, "lxml")
        el = soup.select_one(self._NAME_SELECTOR)
        if el is None:
            return None
        return english_or_none(el.get_text(strip=True))

    def parse(self, soup: BeautifulSoup, url: str) -> DoctorRecord | None:
        name_el = soup.select_one(self._NAME_SELECTOR)
        if name_el is None or not name_el.get_text(strip=True):
            return None
        specialty_ka = None
        spec_el = name_el.find_next_sibling("div")
        if spec_el is not None:
            text = spec_el.get_text(" ", strip=True)
            if text:
                specialty_ka = text
        photo_url = None
        og_image = soup.select_one('meta[property="og:image"]')
        if og_image is not None:
            src = og_image.get("content")
            if src:
                photo_url = urljoin(url, src)
        return DoctorRecord(
            source=self.name,
            source_url=url,
            full_name_ka=name_el.get_text(strip=True),
            full_name_en=self._fetch_english_name(url),
            specialty_ka=specialty_ka,
            photo_url=photo_url,
            clinics=[_HOSPITAL_CLINIC],
        )


register(CmcScraper())
