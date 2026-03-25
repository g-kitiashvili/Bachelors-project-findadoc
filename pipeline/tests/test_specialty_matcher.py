from __future__ import annotations

import psycopg
import pytest

from pipeline.core.specialty_matcher import SpecialtyMatcher


@pytest.fixture()
def matcher_db(postgres_container):
    with psycopg.connect(postgres_container, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE doctor_specialty, specialty RESTART IDENTITY")
        cur.execute(
            "INSERT INTO specialty (slug, name_ka, name_en, sort_order) VALUES "
            "('cardiology', 'კარდიოლოგია', 'Cardiology', 10), "
            "('neurology', 'ნევროლოგია', 'Neurology', 70), "
            "('cardiac-surgery', 'კარდიოქირურგია', 'Cardiac Surgery', 50)"
        )
    yield postgres_container


def test_match_perfect_ka_returns_specialty_id(matcher_db: str) -> None:
    matcher = SpecialtyMatcher(dsn=matcher_db)
    result = matcher.match(token_ka="კარდიოლოგია", token_en=None)
    assert result is not None
    assert result.slug == "cardiology"


def test_match_perfect_en_returns_specialty_id(matcher_db: str) -> None:
    matcher = SpecialtyMatcher(dsn=matcher_db)
    result = matcher.match(token_ka=None, token_en="Cardiology")
    assert result is not None
    assert result.slug == "cardiology"


def test_match_below_threshold_returns_none(matcher_db: str) -> None:
    matcher = SpecialtyMatcher(dsn=matcher_db)
    assert matcher.match(token_ka=None, token_en="completely unrelated string") is None


def test_match_near_match_above_threshold(matcher_db: str) -> None:
    matcher = SpecialtyMatcher(dsn=matcher_db)
    result = matcher.match(token_ka="კარდიოლოგი", token_en=None)
    assert result is not None and result.slug == "cardiology"
