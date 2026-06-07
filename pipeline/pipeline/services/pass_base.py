"""Base class for post-scrape database passes.

A Pass owns a `Database` and exposes a single `run()` entry point that returns a
stats object. The Runner holds an ordered list of passes and runs them after a
scrape cycle; the CLI also runs individual passes standalone.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pipeline.infra.db import Database


class Pass(ABC):
    def __init__(self, dsn: str) -> None:
        self._db = Database(dsn)

    @abstractmethod
    def run(self) -> Any:
        """Execute the pass against the database and return its stats."""
