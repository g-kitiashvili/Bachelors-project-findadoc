"""Single owner of Postgres connection lifecycle.

Every pass, seeder, matcher and the persister holds a `Database` instead of a raw
DSN string and repeating `with psycopg.connect(dsn) as conn, conn.cursor() as cur:`.
psycopg's connection context manager commits on a clean exit and rolls back on an
exception, so callers no longer issue explicit `commit()`.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

import psycopg


class Database:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    @property
    def dsn(self) -> str:
        return self._dsn

    @contextmanager
    def connection(self, *, autocommit: bool = False) -> Iterator[psycopg.Connection]:
        """A connection that commits on clean exit / rolls back on exception."""
        with psycopg.connect(self._dsn, autocommit=autocommit) as conn:
            yield conn

    @contextmanager
    def cursor(self, *, autocommit: bool = False) -> Iterator[psycopg.Cursor]:
        """A cursor on a fresh connection, with the same commit-on-exit semantics."""
        with psycopg.connect(self._dsn, autocommit=autocommit) as conn, conn.cursor() as cur:
            yield cur
