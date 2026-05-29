"""vipmed.ge scraper — Georgian doctor aggregator (per-doctor clinics), static HTTP.

The roster at /doctors/ paginates (/doctors/page/N/) 12 cards per page; each card
carries the profile link, the Georgian name, the specialty, and a photo. discover()
walks the roster, harvesting profile links and recording each doctor's specialty and
photo as it goes (the profile body buries the specialty among unlabelled fields, so
the card is the clean source); parse() reads those back from the discovery map.

vipmed appends "MD" to every doctor's name — stripped via _strip_md before persisting.

vipmed contributes doctors only. Its per-doctor "workplace" lists are free-text role and
affiliation phrases with no clinic URL, riddled with truncations, qualification fragments,
and bare years; too unreliable to yield clean clinic records. Clinics come from the official
clinic sites and tsamali instead. The workplace heading still gates parse() as a profile marker.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from pipeline.core.fetcher import FetchError
from pipeline.core.record import DoctorRecord
from pipeline.core.registry import register
from pipeline.core.static_scraper import StaticHtmlScraper
from pipeline.core.translit import english_or_none


_BASE = "https://vipmed.ge"
_ROSTER = f"{_BASE}/doctors/"
_WORKPLACE_HEADING = re.compile(r"სამუშაო ადგილი")

_DEGREE_SUFFIX = re.compile(r"(?:\s*[,.]?\s*(?:M\.?\s*D|Ph\.?\s*D)\.?)+\s*$", re.IGNORECASE)


def _strip_md(name: str) -> str:
    return _DEGREE_SUFFIX.sub("", name).strip()


def _en_url(url: str) -> str:
    """Insert '-en' before the trailing slash of a vipmed profile URL."""
    return url.rstrip("/") + "-en/"


class VipmedScraper(StaticHtmlScraper):
    name = "vipmed"
    profile_link_selector = "div.team-item h3.team-title a[href]"

    def __init__(self, fetcher=None) -> None:
        super().__init__(fetcher, rate_per_sec=2.0)
        self._specialty_by_url: dict[str, str] = {}
        self._photo_by_url: dict[str, str] = {}

    def _roster_urls(self) -> Iterator[str]:
        page = 1
        while True:
            yield _ROSTER if page == 1 else f"{_BASE}/doctors/page/{page}/"
            page += 1

    def index_urls(self) -> Iterable[str]:
        return self._roster_urls()

    def discover(self) -> Iterator[str]:
        seen: set[str] = set()
        for roster_url in self._roster_urls():
            soup = BeautifulSoup(self.fetcher.get(roster_url), "lxml")
            new_on_page = 0
            for item in soup.select("div.team-item"):
                link = item.select_one("h3.team-title a[href]")
                if link is None:
                    continue
                absolute = urljoin(roster_url, link["href"])
                new_on_page += 1
                dep = item.select_one("div.team-department")
                if dep is not None and dep.get_text(strip=True):
                    self._specialty_by_url[absolute] = dep.get_text(strip=True)
                img = item.select_one("div.team-image img[src]")
                if img is not None:
                    self._photo_by_url[absolute] = urljoin(roster_url, img["src"])
                if absolute in seen:
                    continue
                seen.add(absolute)
                yield absolute
            if new_on_page == 0:
                break

    def parse(self, soup: BeautifulSoup, url: str) -> DoctorRecord | None:
        if soup.find(["h2", "h3"], string=_WORKPLACE_HEADING) is None:
            return None
        name_el = soup.find("h1")
        if name_el is None:
            return None
        name = _strip_md(name_el.get_text(strip=True))
        if not name:
            return None
        full_name_en: str | None = None
        try:
            en_soup = BeautifulSoup(self.fetcher.get(_en_url(url)), "lxml")
            en_h1 = en_soup.find("h1")
            if en_h1 is not None:
                full_name_en = english_or_none(_strip_md(en_h1.get_text(strip=True)))
        except FetchError:
            pass
        return DoctorRecord(
            source=self.name,
            source_url=url,
            full_name_ka=name,
            full_name_en=full_name_en,
            specialty_ka=self._specialty_by_url.get(url),
            photo_url=self._photo_by_url.get(url),
        )


register(VipmedScraper())
