"""vivomedical.ge scraper (Vivo Medical Group, Tbilisi) — static HTML via httpx."""

from __future__ import annotations

import re
from collections.abc import Iterator

from bs4 import BeautifulSoup

from pipeline.core.record import DoctorRecord
from pipeline.core.registry import register
from pipeline.core.static_scraper import StaticHtmlScraper

_BG_URL_RE = re.compile(r"url\(['\"]?(//[^'\")\s]+)['\"]?\)")
_CLINIC_RE = re.compile(r"clinic=(\d+)")


class VivomedicalScraper(StaticHtmlScraper):
    name = "vivomedical"
    profile_link_selector = "a.card__doctor"
    _INDEX_URL = "https://vivomedical.ge/ge/19"
    _NAME_SELECTOR = "h2.title"
    _SPECIALTY_SELECTOR = "span.position"
    _PHOTO_DIV_SELECTOR = "div.doctordetails__info div.primary-info div.image"

    def __init__(self, fetcher=None) -> None:
        super().__init__(fetcher, rate_per_sec=2.0)

    def index_urls(self) -> Iterator[str]:
        soup = BeautifulSoup(self.fetcher.get(self._INDEX_URL), "lxml")
        yield self._INDEX_URL
        seen_clinics: set[str] = set()
        for anchor in soup.select("a[href*='clinic=']"):
            match = _CLINIC_RE.search(anchor.get("href") or "")
            if match and match.group(1) not in seen_clinics:
                seen_clinics.add(match.group(1))
                yield f"{self._INDEX_URL}?clinic={match.group(1)}"

    def parse(self, soup: BeautifulSoup, url: str) -> DoctorRecord | None:
        name_el = soup.select_one(self._NAME_SELECTOR)
        if name_el is None or not name_el.get_text(strip=True):
            return None
        specialty_el = next(
            (el for el in soup.select(self._SPECIALTY_SELECTOR) if el.get_text(strip=True)),
            None,
        )
        photo_url = None
        photo_div = soup.select_one(self._PHOTO_DIV_SELECTOR)
        if photo_div is not None:
            style = photo_div.get("style", "")
            m = _BG_URL_RE.search(style)
            if m:
                photo_url = f"https:{m.group(1)}"
        return DoctorRecord(
            source=self.name,
            source_url=url,
            full_name_ka=name_el.get_text(strip=True),
            specialty_ka=specialty_el.get_text(strip=True) if specialty_el else None,
            photo_url=photo_url or None,
        )


register(VivomedicalScraper())
