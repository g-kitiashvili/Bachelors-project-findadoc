"""joann.ge scraper — Jo Ann University Hospital (Tbilisi), static WordPress/Elementor HTML via httpx."""

from __future__ import annotations

import re
from collections.abc import Iterator
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from pipeline.core.record import ClinicRef, DoctorRecord
from pipeline.core.registry import register
from pipeline.core.static_scraper import StaticHtmlScraper

_HOSPITAL_CLINIC = ClinicRef(
    source_url="https://joann.ge", name_ka="ჯო ენის საუნივერსიტეტო ჰოსპიტალი"
)

_PROFILE_HREF = re.compile(r"^https://joann\.ge/eqimebi/[^/]+/?$")
_INDEX_HREF = "https://joann.ge/eqimebi/"


class JoannScraper(StaticHtmlScraper):
    name = "joann"
    profile_link_selector = 'a[href*="/eqimebi/"]'
    _INDEX_URL = "https://joann.ge/eqimebi/"

    def __init__(self, fetcher=None) -> None:
        super().__init__(fetcher, rate_per_sec=2.0)

    def index_urls(self) -> Iterator[str]:
        yield self._INDEX_URL

    def discover(self) -> Iterator[str]:
        seen: set[str] = set()
        for index_url in self.index_urls():
            soup = BeautifulSoup(self.fetcher.get(index_url), "lxml")
            new_on_page = 0
            for a in soup.select(self.profile_link_selector):
                href = a.get("href")
                if not href:
                    continue
                absolute = urljoin(index_url, href).rstrip("/")
                if absolute == _INDEX_HREF.rstrip("/"):
                    continue
                if not _PROFILE_HREF.match(href):
                    continue
                if absolute in seen:
                    continue
                seen.add(absolute)
                new_on_page += 1
                yield absolute
            if new_on_page == 0:
                break

    def parse(self, soup: BeautifulSoup, url: str) -> DoctorRecord | None:
        heading = soup.select_one("div.elementor-widget-heading h1")
        if heading is None or not heading.get_text(strip=True):
            return None
        specialty_ka = self._specialty(heading)
        if specialty_ka is None:
            return None
        photo_url = None
        og_image = soup.select_one('meta[property="og:image"]')
        if og_image is not None:
            src = og_image.get("content")
            if src:
                photo_url = urljoin(url, src)
        return DoctorRecord(
            source=self.name,
            source_url=url,
            full_name_ka=heading.get_text(strip=True),
            specialty_ka=specialty_ka,
            photo_url=photo_url,
            clinics=[_HOSPITAL_CLINIC],
        )

    @staticmethod
    def _specialty(heading) -> str | None:
        heading_widget = heading.find_parent("div", class_="elementor-widget-heading")
        column = (heading_widget or heading).find_parent("div", class_="elementor-column")
        if column is None:
            return None
        passed_heading = False
        for widget in column.select("div.elementor-widget"):
            if widget is heading_widget:
                passed_heading = True
                continue
            if passed_heading and "elementor-widget-wd_title" in (widget.get("class") or []):
                text = widget.get_text(" ", strip=True)
                if text:
                    return text
        return None


register(JoannScraper())
