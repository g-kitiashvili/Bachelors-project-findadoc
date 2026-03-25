"""Shared pytest fixtures — Testcontainers Postgres applying the api Flyway migrations."""

from __future__ import annotations

from pathlib import Path

import psycopg
import pytest
from testcontainers.postgres import PostgresContainer


_MIGRATIONS_DIR = (
    Path(__file__).resolve().parent.parent.parent / "api" / "src" / "main" / "resources" / "db" / "migration"
)


def _apply_migrations(dsn: str) -> None:
    files = sorted(_MIGRATIONS_DIR.glob("V*.sql"))
    if not files:
        raise RuntimeError(f"no Flyway migrations found at {_MIGRATIONS_DIR}")
    with psycopg.connect(dsn, autocommit=True) as conn:
        for f in files:
            sql = f.read_text(encoding="utf-8")
            conn.execute(sql)


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16-alpine", driver=None) as pg:
        dsn = (
            f"host={pg.get_container_host_ip()} "
            f"port={pg.get_exposed_port(5432)} "
            f"dbname={pg.dbname} "
            f"user={pg.username} "
            f"password={pg.password}"
        )
        _apply_migrations(dsn)
        yield dsn


@pytest.fixture()
def clean_doctor_table(postgres_container):
    with psycopg.connect(postgres_container, autocommit=True) as conn:
        conn.execute("TRUNCATE doctor_specialty, doctor RESTART IDENTITY")
    yield postgres_container
