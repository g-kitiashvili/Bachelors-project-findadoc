"""aversiclinic.ge scraper — uses Playwright+stealth+8s wait (Cloudflare bypass).

Note: aversi.ge is the pharmacy chain; aversiclinic.ge hosts the doctor directory.

EN coverage is partial — only ~40% of doctors have actual English content.
extract() opportunistically fetches the /en/ counterpart per doctor and populates
full_name_en + bio_en if a distinct English page exists. Otherwise the runner's
translit.normalize() step fills full_name_en from the placeholder transliterator.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from pipeline.core.fetcher import FetchError, PlaywrightFetcher
from pipeline.core.record import ClinicRef, DoctorRecord
from pipeline.core.registry import register

_BRAND_CLINIC = ClinicRef(source_url="https://aversi.ge", name_ka="ავერსის კლინიკა")


class AversiScraper:
    name = "aversi"
    _BASE = "https://aversiclinic.ge"
    _KA_INDEX = "https://aversiclinic.ge/doctors"
    _PROFILE_LINK_SELECTOR = "a.doctor-card"
    _NAME_SELECTOR = ".text-content__title"
    _SPECIALTY_SELECTOR = ".text-content__subtitle"
    _PHOTO_SELECTOR = "meta[property='og:image']"
    _BIO_SELECTOR = ".doctor-render-list"

    def __init__(self, fetcher=None, *, max_pages: int = 2) -> None:
        # `max_pages` caps discover() pagination. Default 2 (~32 doctors) keeps the
        # demo runtime reasonable. Production cron can pass a larger value
        # (e.g., 30 for the full ~480 doctors).
        self.fetcher = fetcher or PlaywrightFetcher(
            rate_per_sec=0.5, headless=False, stealth=True, cf_wait_ms=8000
        )
        self._max_pages = max_pages

    def discover(self) -> Iterator[str]:
        seen: set[str] = set()
        for page in range(1, self._max_pages + 1):
            index_url = f"{self._BASE}/doctors/{page}"
            try:
                html = self.fetcher.get(index_url)
            except FetchError:
                break  # pagination ran past the end
            soup = BeautifulSoup(html, "lxml")
            cards = soup.select(self._PROFILE_LINK_SELECTOR)
            if not cards:
                break  # empty page → no more pagination
            new_in_page = 0
            for a in cards:
                href = a.get("href")
                if not href:
                    continue
                absolute = urljoin(self._BASE, href)
                if absolute in seen:
                    continue
                seen.add(absolute)
                new_in_page += 1
                yield absolute
            # Safety: if a page has cards but ALL are already seen, stop
            if new_in_page == 0:
                break

    def extract(self, html: str, url: str) -> DoctorRecord | None:
        soup = BeautifulSoup(html, "lxml")

        name_el = soup.select_one(self._NAME_SELECTOR)
        if name_el is None or not name_el.get_text(strip=True):
            return None

        primary_name = name_el.get_text(strip=True)

        specialty_el = soup.select_one(self._SPECIALTY_SELECTOR)
        primary_specialty = specialty_el.get_text(strip=True) if specialty_el is not None else None

        photo_url = None
        photo_el = soup.select_one(self._PHOTO_SELECTOR)
        if photo_el is not None:
            content = photo_el.get("content")
            if content:
                photo_url = urljoin(url, content)

        bio_el = soup.select_one(self._BIO_SELECTOR)
        primary_bio = bio_el.get_text(separator="\n", strip=True) if bio_el is not None else None

        # If the URL is already an EN URL, primary_name is English; treat that as full_name_en
        # and leave full_name_ka unknown. (Defensive — discover yields KA URLs.)
        if "/en/" in url:
            return DoctorRecord(
                source=self.name,
                source_url=url,
                full_name_ka=primary_name,  # best-effort
                full_name_en=primary_name,
                photo_url=photo_url,
                bio_en=primary_bio,
                specialty_en=primary_specialty,
                clinics=[_BRAND_CLINIC],
            )

        # Normal path: url is a KA URL. Try the EN counterpart opportunistically.
        full_name_en = None
        bio_en = None
        specialty_en = None
        en_url = self._derive_en_url(url)
        if en_url:
            try:
                en_html = self.fetcher.get(en_url)
            except FetchError:
                en_html = None
            if en_html is not None:
                en_soup = BeautifulSoup(en_html, "lxml")
                en_name_el = en_soup.select_one(self._NAME_SELECTOR)
                if en_name_el is not None:
                    candidate = en_name_el.get_text(strip=True)
                    # Reject if the EN response served the KA name (redirect back to KA)
                    if candidate and candidate != primary_name:
                        full_name_en = candidate
                        en_bio_el = en_soup.select_one(self._BIO_SELECTOR)
                        if en_bio_el is not None:
                            bio_en = en_bio_el.get_text(separator="\n", strip=True)
                        en_specialty_el = en_soup.select_one(self._SPECIALTY_SELECTOR)
                        if en_specialty_el is not None:
                            specialty_en = en_specialty_el.get_text(strip=True) or None

        return DoctorRecord(
            source=self.name,
            source_url=url,
            full_name_ka=primary_name,
            full_name_en=full_name_en,
            photo_url=photo_url,
            bio_ka=primary_bio,
            bio_en=bio_en,
            specialty_ka=primary_specialty,
            specialty_en=specialty_en,
            clinics=[_BRAND_CLINIC],
        )

    @staticmethod
    def _derive_en_url(ka_url: str) -> str | None:
        """Inject /en/ after the host. None if URL already has /en/."""
        if "/en/" in ka_url:
            return None
        return re.sub(r"^(https://[^/]+)/doctors/", r"\1/en/doctors/", ka_url, count=1)


# Self-register on import.
register(AversiScraper())
