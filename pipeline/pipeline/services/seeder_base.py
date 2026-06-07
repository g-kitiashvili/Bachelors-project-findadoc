"""Base class for reference-data seeders.

A Seeder owns a `Database` and a source YAML path, and exposes `seed()` which
upserts its reference rows and returns the top-level row count. The Runner holds
an ordered list of seeders and runs them before scraping (order matters:
conditions resolve onto specialties, so specialties seed first).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from pipeline.infra.db import Database


class Seeder(ABC):
    def __init__(self, *, dsn: str, yaml_path: Path | str) -> None:
        self._db = Database(dsn)
        self._yaml_path = Path(yaml_path)

    @abstractmethod
    def seed(self) -> int:
        """Upsert reference rows from YAML and return the number of top-level rows."""
