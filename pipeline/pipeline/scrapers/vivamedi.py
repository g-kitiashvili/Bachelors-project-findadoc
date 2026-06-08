"""vivamedi.ge scraper (Medical Center Vivamedi, Tbilisi) - static HTML via httpx.

Old OpenCart site, server-rendered XHTML, no JSON API. Fetched over http to avoid
the site's expired TLS certificate (https fails verification, http serves 200).
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from urllib.parse import quote, urljoin

from bs4 import BeautifulSoup

from pipeline.domain.record import ClinicRef, DoctorRecord
from pipeline.scrapers.registry import register
from pipeline.scrapers.static_scraper import StaticHtmlScraper

_PAGE_RE = re.compile(r"[?&]page=(\d+)")

_BRAND_CLINIC = ClinicRef(
    source_url="http://vivamedi.ge",
    name_ka="სამედიცინო ცენტრი ვივამედი",
    name_en="Medical Center Vivamedi",
    address="საქართველო, თბილისი, აღმაშენებლის ხეივანი N234, ნაკვეთი 14/470",
    phone="+995 32 2 101 100",
)


class VivamediScraper(StaticHtmlScraper):
    name = "vivamedi"
    profile_link_selector = "a[href*='doctor_id=']"
    _INDEX_URL = "http://vivamedi.ge/doctors"

    def __init__(self, fetcher=None) -> None:
        super().__init__(fetcher, rate_per_sec=2.0)

    def index_urls(self) -> Iterator[str]:
        yield self._INDEX_URL
        soup = BeautifulSoup(self.fetcher.get(self._INDEX_URL), "lxml")
        seen: set[int] = set()
        for anchor in soup.select("a[href*='page=']"):
            match = _PAGE_RE.search(anchor.get("href") or "")
            if match is None:
                continue
            page = int(match.group(1))
            if page < 2 or page in seen:
                continue
            seen.add(page)
            yield f"{self._INDEX_URL}?page={page}"

    def parse(self, soup: BeautifulSoup, url: str) -> DoctorRecord | None:
        name_el = soup.select_one(".memberInfo h3")
        if name_el is None or not name_el.get_text(strip=True):
            return None
        specialty_el = soup.select_one(".memberInfo .position")
        img = soup.select_one(".first_image img") or soup.select_one("img[src*='/image/cache/data/']")
        photo_url = None
        if img is not None and img.get("src"):
            photo_url = quote(urljoin(url, img["src"]), safe=":/?&=#%")
        bio = None
        bio_el = soup.select_one(".leftContent .allNews")
        if bio_el is not None:
            text = re.sub(r"^ექიმები\s+", "", bio_el.get_text(" ", strip=True))
            bio = text or None
        return DoctorRecord(
            source=self.name,
            source_url=url,
            full_name_ka=name_el.get_text(" ", strip=True),
            specialty_ka=specialty_el.get_text(" ", strip=True) if specialty_el else None,
            photo_url=photo_url,
            bio_ka=bio,
            clinics=(_BRAND_CLINIC,),
        )


register(VivamediScraper())
