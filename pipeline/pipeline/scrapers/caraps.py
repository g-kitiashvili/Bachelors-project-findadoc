"""carapsmedline.ge scraper — Caraps Medline (Tbilisi hospital).

The doctor roster is an SPA fed by a POST endpoint (/doctors/filter) that
returns an HTML grid fragment, so discover() posts page-by-page to harvest
profile links; each profile page is static SSR HTML parsed by httpx.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from pipeline.infra.fetcher import FetchError
from pipeline.domain.record import ClinicRef, DoctorRecord
from pipeline.scrapers.registry import register
from pipeline.scrapers.static_scraper import StaticHtmlScraper
from pipeline.domain.translit import english_or_none

_HOSPITAL_CLINIC = ClinicRef(
    source_url="https://carapsmedline.ge",
    name_ka="კარაპს მედლაინი",
    name_en="Caraps Medline",
)

_BASE = "https://carapsmedline.ge"
_FILTER_URL = f"{_BASE}/doctors/filter"
_PAGE_SIZE = 12
_PROFILE_HREF = re.compile(r"^https://carapsmedline\.ge/doctors/[^/?#]+$")


class CarapsScraper(StaticHtmlScraper):
    name = "caraps"
    profile_link_selector = "a.grid-item"

    def __init__(self, fetcher=None) -> None:
        super().__init__(fetcher, rate_per_sec=2.0)

    def _grid_html(self, page: int) -> str:
        raw = self.fetcher.post(
            _FILTER_URL,
            data={"searchPhrase": "", "specialtyID": "", "page": page, "pageSize": _PAGE_SIZE},
            headers={"X-Requested-With": "XMLHttpRequest"},
        )
        return (json.loads(raw).get("Data") or {}).get("DoctorsGridHtml") or ""

    def discover(self) -> Iterator[str]:
        seen: set[str] = set()
        page = 1
        while True:
            soup = BeautifulSoup(self._grid_html(page), "lxml")
            new_on_page = 0
            for a in soup.select(self.profile_link_selector):
                href = a.get("href")
                if not href:
                    continue
                absolute = urljoin(_BASE, href)
                if not _PROFILE_HREF.match(absolute) or absolute in seen:
                    continue
                seen.add(absolute)
                new_on_page += 1
                yield absolute
            if new_on_page == 0:
                break
            page += 1

    def index_urls(self) -> Iterator[str]:
        raise NotImplementedError("caraps discovery uses the /doctors/filter POST endpoint")

    def parse(self, soup: BeautifulSoup, url: str) -> DoctorRecord | None:
        head = soup.select_one("div.page-head")
        if head is None:
            return None
        name_el = head.select_one("div.info-col h1.title")
        if name_el is None or not name_el.get_text(strip=True):
            return None
        specialty_ka = None
        spec_el = head.select_one("div.info-col div.text-wrap")
        if spec_el is not None:
            text = spec_el.get_text(" ", strip=True)
            if text:
                specialty_ka = text
        photo_url = None
        img = head.select_one("div.img-col img")
        if img is not None:
            src = img.get("src")
            if src:
                photo_url = urljoin(url, src)
        full_name_en = None
        en_url = url.replace(
            "https://carapsmedline.ge/doctors/",
            "https://carapsmedline.ge/en/doctors/",
            1,
        )
        if en_url != url:
            try:
                en_html = self.fetcher.get(en_url)
                en_soup = BeautifulSoup(en_html, "lxml")
                en_el = en_soup.select_one("div.info-col h1.title")
                if en_el is not None:
                    full_name_en = english_or_none(en_el.get_text(strip=True))
            except FetchError:
                pass
        return DoctorRecord(
            source=self.name,
            source_url=url,
            full_name_ka=name_el.get_text(strip=True),
            full_name_en=full_name_en,
            specialty_ka=specialty_ka,
            photo_url=photo_url,
            clinics=[_HOSPITAL_CLINIC],
        )


register(CarapsScraper())
