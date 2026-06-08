"""newhospitals.ge scraper — static HTML via httpx."""

from __future__ import annotations

from collections.abc import Iterable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from pipeline.infra.fetcher import FetchError
from pipeline.domain.record import ClinicRef, DoctorRecord
from pipeline.scrapers.registry import register
from pipeline.scrapers.static_scraper import StaticHtmlScraper
from pipeline.domain.translit import english_or_none

_BRAND_CLINIC = ClinicRef(source_url="https://newhospitals.ge", name_ka="ნიუ ჰოსპიტალსი", name_en="New Hospitals")


class NewhospitalsScraper(StaticHtmlScraper):
    name = "newhospitals"
    profile_link_selector = "a.doctor__block"
    _INDEX_URL = "https://newhospitals.ge/ka/doctors"
    _NAME_SELECTOR = "h2.doctor-inner__name"
    _PHOTO_SELECTOR = "div.doctor-inner__img img"
    _BIO_SELECTOR = "div.text-holder"

    def index_urls(self) -> Iterable[str]:
        return [self._INDEX_URL]

    def parse(self, soup: BeautifulSoup, url: str) -> DoctorRecord | None:
        name_el = soup.select_one(self._NAME_SELECTOR)
        if name_el is None or not name_el.get_text(strip=True):
            return None
        photo_url = None
        photo_el = soup.select_one(self._PHOTO_SELECTOR)
        if photo_el is not None:
            src = photo_el.get("src") or photo_el.get("data-src")
            if src:
                photo_url = urljoin(url, src)
        specialty_ka = None
        bio_ka = None
        bio_el = soup.select_one(self._BIO_SELECTOR)
        if bio_el is not None:
            first_p = bio_el.find("p")
            if first_p is not None and first_p.get_text(strip=True):
                specialty_ka = first_p.get_text(strip=True)
            ul_texts = [ul.get_text(separator="\n", strip=True) for ul in bio_el.find_all("ul")]
            bio_ka = "\n".join(t for t in ul_texts if t) or None
        full_name_en = None
        en_url = url.replace("/ka/", "/en/", 1) if "/ka/" in url else None
        if en_url is not None:
            try:
                en_html = self.fetcher.get(en_url)
                en_soup = BeautifulSoup(en_html, "lxml")
                en_el = en_soup.select_one(self._NAME_SELECTOR)
                if en_el is not None:
                    full_name_en = english_or_none(en_el.get_text(strip=True))
            except FetchError:
                pass
        return DoctorRecord(
            source=self.name,
            source_url=url,
            full_name_ka=name_el.get_text(strip=True),
            full_name_en=full_name_en,
            photo_url=photo_url,
            bio_ka=bio_ka,
            specialty_ka=specialty_ka,
            clinics=[_BRAND_CLINIC],
        )


register(NewhospitalsScraper())
