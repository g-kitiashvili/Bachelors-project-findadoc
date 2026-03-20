"""newhospitals.ge scraper — HTTP-only via httpx (no JS needed)."""

from __future__ import annotations

from collections.abc import Iterator
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from pipeline.core.fetcher import HttpxFetcher
from pipeline.core.record import DoctorRecord
from pipeline.core.registry import register


class NewhospitalsScraper:
    name = "newhospitals"
    _INDEX_URL = "https://newhospitals.ge/ka/doctors"
    _PROFILE_LINK_SELECTOR = "a.doctor__block"
    _NAME_SELECTOR = "h2.doctor-inner__name"
    _PHOTO_SELECTOR = "div.doctor-inner__img img"
    _BIO_SELECTOR = "div.text-holder"
    # Specialty extraction strategy: in the static HTML (JS-rendered specialty is absent),
    # the specialty text is the FIRST <p> inside div.text-holder. The bio bullet-points
    # follow in <ul> elements. We extract them separately rather than merging all text.
    _SPECIALTY_FROM_BIO = True  # flag documents the extraction approach

    def __init__(self, fetcher=None) -> None:
        self.fetcher = fetcher or HttpxFetcher(rate_per_sec=1.0)

    def discover(self) -> Iterator[str]:
        html = self.fetcher.get(self._INDEX_URL)
        soup = BeautifulSoup(html, "lxml")
        seen: set[str] = set()
        for a in soup.select(self._PROFILE_LINK_SELECTOR):
            href = a.get("href")
            if not href:
                continue
            absolute = urljoin(self._INDEX_URL, href)
            if absolute in seen:
                continue
            seen.add(absolute)
            yield absolute

    def extract(self, html: str, url: str) -> DoctorRecord | None:
        soup = BeautifulSoup(html, "lxml")

        name_el = soup.select_one(self._NAME_SELECTOR)
        if name_el is None or not name_el.get_text(strip=True):
            return None

        full_name_ka = name_el.get_text(strip=True)

        photo_url = None
        photo_el = soup.select_one(self._PHOTO_SELECTOR)
        if photo_el is not None:
            src = photo_el.get("src") or photo_el.get("data-src")
            if src:
                photo_url = urljoin(url, src)

        # Specialty and bio are both inside div.text-holder.
        # The first <p> child is the specialty; <ul> elements are the bio bullet-points.
        specialty_ka = None
        bio_ka = None
        bio_el = soup.select_one(self._BIO_SELECTOR)
        if bio_el is not None:
            first_p = bio_el.find("p")
            if first_p is not None:
                specialty_text = first_p.get_text(strip=True)
                if specialty_text:
                    specialty_ka = specialty_text
            # Bio: collect text from all <ul> elements in text-holder
            ul_texts = [
                ul.get_text(separator="\n", strip=True)
                for ul in bio_el.find_all("ul")
            ]
            bio_ka = "\n".join(t for t in ul_texts if t) or None

        return DoctorRecord(
            source=self.name,
            source_url=url,
            full_name_ka=full_name_ka,
            photo_url=photo_url,
            bio_ka=bio_ka,
            specialty_ka=specialty_ka,
        )


# Self-register on import.
register(NewhospitalsScraper())
