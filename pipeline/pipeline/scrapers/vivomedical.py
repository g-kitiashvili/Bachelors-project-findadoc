"""vivomedical.ge scraper (Vivo Medical Group, Tbilisi) — static HTML via httpx."""

from __future__ import annotations

import re
from collections.abc import Iterator
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from pipeline.infra.fetcher import FetchError
from pipeline.domain.record import ClinicRef, DoctorRecord
from pipeline.scrapers.registry import register
from pipeline.scrapers.static_scraper import StaticHtmlScraper
from pipeline.domain.translit import english_or_none

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

    _CLINIC_LINK_SELECTOR = "a[href*='/ge/16/']"
    _CLINIC_LINK_EN_SELECTOR = "a[href*='/en/16/']"
    _CLINIC_NAME_SELECTOR = "h4.title"
    _CLINIC_ADDRESS_SELECTOR = "p.texticon.address span"
    _CLINIC_PHONE_SELECTOR = "p.texticon.phone span"

    def _clinics(
        self, soup: BeautifulSoup, url: str, en_soup: BeautifulSoup | None = None
    ) -> list[ClinicRef]:
        link = soup.select_one(self._CLINIC_LINK_SELECTOR)
        if link is None:
            return []
        href = link.get("href")
        name_el = link.select_one(self._CLINIC_NAME_SELECTOR)
        name = name_el.get_text(" ", strip=True) if name_el else link.get_text(" ", strip=True)
        if not name or not href:
            return []
        clinic_url = urljoin("https:" if href.startswith("//") else url, href)
        addr_el = link.select_one(self._CLINIC_ADDRESS_SELECTOR)
        address = addr_el.get_text(" ", strip=True) if addr_el else None
        phone_el = link.select_one(self._CLINIC_PHONE_SELECTOR)
        phone = phone_el.get_text(" ", strip=True) if phone_el else None
        name_en: str | None = None
        if en_soup is not None:
            en_link = en_soup.select_one(self._CLINIC_LINK_EN_SELECTOR)
            if en_link is not None:
                en_name_el = en_link.select_one(self._CLINIC_NAME_SELECTOR)
                en_text = en_name_el.get_text(" ", strip=True) if en_name_el else None
                name_en = english_or_none(en_text)
        return [ClinicRef(source_url=clinic_url, name_ka=name, name_en=name_en, address=address or None, phone=phone or None)]

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
        en_soup: BeautifulSoup | None = None
        full_name_en: str | None = None
        if "/ge/" in url:
            en_url = url.replace("/ge/", "/en/", 1)
            try:
                en_html = self.fetcher.get(en_url)
                en_soup = BeautifulSoup(en_html, "lxml")
                en_name_el = en_soup.select_one(self._NAME_SELECTOR)
                full_name_en = english_or_none(
                    en_name_el.get_text(strip=True) if en_name_el else None
                )
            except (FetchError, KeyError):
                pass
        return DoctorRecord(
            source=self.name,
            source_url=url,
            full_name_ka=name_el.get_text(strip=True),
            full_name_en=full_name_en,
            specialty_ka=specialty_el.get_text(strip=True) if specialty_el else None,
            photo_url=photo_url or None,
            clinics=self._clinics(soup, url, en_soup),
        )


register(VivomedicalScraper())
