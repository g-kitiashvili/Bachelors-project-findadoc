"""StaticHtmlScraper — Template-Method base for static-HTML, httpx-backed scrapers.

Holds the shared discover() (walk index_urls(), harvest profile links, dedupe)
and the BeautifulSoup boilerplate of extract(). Subclasses supply index_urls(),
the profile-link selector, and per-profile parse(). Conforms to the Scraper
Protocol in core/scraper.py; Playwright/odd sources implement Scraper directly.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from pipeline.infra.fetcher import Fetcher, HttpxFetcher
from pipeline.domain.record import DoctorRecord


class StaticHtmlScraper(ABC):
    name: str
    profile_link_selector: str

    def __init__(self, fetcher: Fetcher | None = None, *, rate_per_sec: float = 1.0) -> None:
        self.fetcher = fetcher or HttpxFetcher(rate_per_sec=rate_per_sec)

    @abstractmethod
    def index_urls(self) -> Iterable[str]:
        """Listing pages to harvest profile links from."""

    @abstractmethod
    def parse(self, soup: BeautifulSoup, url: str) -> DoctorRecord | None:
        """Parse one profile page into a DoctorRecord (or None if not a profile)."""

    def discover(self) -> Iterator[str]:
        seen: set[str] = set()
        for index_url in self.index_urls():
            soup = BeautifulSoup(self.fetcher.get(index_url), "lxml")
            for a in soup.select(self.profile_link_selector):
                href = a.get("href")
                if not href:
                    continue
                absolute = urljoin(index_url, href)
                if absolute in seen:
                    continue
                seen.add(absolute)
                yield absolute

    def extract(self, html: str, url: str) -> DoctorRecord | None:
        return self.parse(BeautifulSoup(html, "lxml"), url)
