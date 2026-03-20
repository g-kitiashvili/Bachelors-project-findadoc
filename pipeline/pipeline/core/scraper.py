"""Scraper protocol — what each source-specific module must implement."""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from pipeline.core.record import DoctorRecord

if TYPE_CHECKING:  # avoid runtime circular import; fetcher.py is independent
    from pipeline.core.fetcher import Fetcher


@runtime_checkable
class Scraper(Protocol):
    """Strategy-pattern interface. One implementation per source.

    Each scraper carries its own `fetcher` instance (HttpxFetcher for friendly
    sites, PlaywrightFetcher for Cloudflare-protected sites). `discover` yields
    profile URLs (using its own fetcher for the index). `extract` parses one
    profile's HTML into a DoctorRecord, or None for unsupported pages. The
    `Runner` reads `scraper.fetcher.get(url)` to fetch each profile.
    """

    name: str
    fetcher: "Fetcher"  # forward-declared via TYPE_CHECKING; duck-typed at runtime

    def discover(self) -> Iterator[str]: ...

    def extract(self, html: str, url: str) -> DoctorRecord | None: ...
