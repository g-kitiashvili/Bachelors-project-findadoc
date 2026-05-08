"""vipmed.ge scraper — Georgian doctor aggregator (per-doctor clinics), static HTTP.

The roster at /doctors/ paginates (/doctors/page/N/) 12 cards per page; each card
carries the profile link, the Georgian name, the specialty, and a photo. discover()
walks the roster, harvesting profile links and recording each doctor's specialty and
photo as it goes (the profile body buries the specialty among unlabelled fields, so
the card is the clean source); parse() reads those back from the discovery map.

vipmed appends "MD" to every doctor's name — stripped via _strip_md before persisting.

As an aggregator each doctor lists their own workplace clinics (free text, one per
<li> under the "სამუშაო ადგილი/თანამდებობა" heading). vipmed gives no clinic URL, so
a stable clinic source_url is derived from the clinic name via slugify.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from pipeline.core.record import ClinicRef, DoctorRecord
from pipeline.core.registry import register
from pipeline.core.static_scraper import StaticHtmlScraper
from pipeline.core.translit import slugify


_BASE = "https://vipmed.ge"
_ROSTER = f"{_BASE}/doctors/"
_WORKPLACE_HEADING = re.compile(r"სამუშაო ადგილი")
_CLINIC_NAME_SPLIT = re.compile(r"\s*[–—]\s*|\s*,\s*")

_DEGREE_SUFFIX = re.compile(r"(?:\s*[,.]?\s*(?:M\.?\s*D|Ph\.?\s*D)\.?)+\s*$", re.IGNORECASE)


def _strip_md(name: str) -> str:
    return _DEGREE_SUFFIX.sub("", name).strip()


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

    def _clinics(self, soup: BeautifulSoup) -> list[ClinicRef]:
        heading = soup.find(["h2", "h3"], string=_WORKPLACE_HEADING)
        if heading is None:
            return []
        widget = heading.find_parent(class_="elementor-widget")
        if widget is None:
            return []
        clinics: list[ClinicRef] = []
        seen: set[str] = set()
        block = widget
        while True:
            block = block.find_next(class_="elementor-widget")
            if block is None:
                break
            if not str(block.get("data-widget_type", "")).startswith("text-editor"):
                continue
            for li in block.select("li"):
                raw = li.get_text(" ", strip=True)
                name = _CLINIC_NAME_SPLIT.split(raw, maxsplit=1)[0].strip(" ;.")
                if not name:
                    continue
                source_url = f"{_BASE}/clinic/{slugify(name)}"
                if source_url in seen:
                    continue
                seen.add(source_url)
                clinics.append(ClinicRef(source_url=source_url, name_ka=name))
            break
        return clinics

    def parse(self, soup: BeautifulSoup, url: str) -> DoctorRecord | None:
        if soup.find(["h2", "h3"], string=_WORKPLACE_HEADING) is None:
            return None
        name_el = soup.find("h1")
        if name_el is None:
            return None
        name = _strip_md(name_el.get_text(strip=True))
        if not name:
            return None
        return DoctorRecord(
            source=self.name,
            source_url=url,
            full_name_ka=name,
            specialty_ka=self._specialty_by_url.get(url),
            photo_url=self._photo_by_url.get(url),
            clinics=self._clinics(soup),
        )


register(VipmedScraper())
