"""Single source of truth for which scrapers exist.

Populated in pipeline/scrapers/__init__.py (which imports each scraper
module and registers it here). Other modules import this without creating
import cycles.
"""

from __future__ import annotations

from pipeline.core.scraper import Scraper


SCRAPERS: dict[str, Scraper] = {}


def register(scraper: Scraper) -> None:
    if scraper.name in SCRAPERS:
        raise ValueError(f"scraper {scraper.name!r} already registered")
    SCRAPERS[scraper.name] = scraper


def get_scraper(name: str) -> Scraper:
    if name not in SCRAPERS:
        raise KeyError(f"unknown scraper: {name!r}; known={sorted(SCRAPERS)}")
    return SCRAPERS[name]
