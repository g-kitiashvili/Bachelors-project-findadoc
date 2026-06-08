from __future__ import annotations

import psycopg
import pytest

from pipeline.services.specialty_matcher import SpecialtyMatcher, tokenize
from pipeline.domain.taxonomy import normalize_alias


@pytest.fixture()
def matcher_db(postgres_container):
    with psycopg.connect(postgres_container, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE condition_specialty, doctor_specialty, specialty RESTART IDENTITY CASCADE")
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


def test_match_whole_maps_hyphen_compound_to_child(matcher_db: str) -> None:
    with psycopg.connect(matcher_db, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO specialty (slug, name_ka, name_en, sort_order) VALUES "
            "('surgery', 'ქირურგია', 'Surgery', 49), "
            "('maxillofacial-surgery', 'ყბა-სახის ქირურგია', 'Maxillofacial Surgery', 52)"
        )
    aliases = {normalize_alias("ყბა-სახის ქირურგი"): "maxillofacial-surgery"}
    matcher = SpecialtyMatcher(dsn=matcher_db, aliases=aliases)
    result = matcher.match_whole(raw_ka="ყბა-სახის ქირურგი", raw_en=None)
    assert result is not None and result.slug == "maxillofacial-surgery"
    # the tokenizer would split this compound apart, which is why whole-match runs first
    assert "ყბა" in tokenize("ყბა-სახის ქირურგი")


def test_match_whole_returns_none_without_alias(matcher_db: str) -> None:
    matcher = SpecialtyMatcher(dsn=matcher_db)
    assert matcher.match_whole(raw_ka="კარდიოლოგი", raw_en=None) is None


def test_tokenize_splits_on_en_dash():
    assert tokenize("ექიმი – თერაპევტი") == ["ექიმი", "თერაპევტი"]


def test_tokenize_drops_degree_markers():
    assert tokenize("MD, PhD, კარდიოლოგია") == ["კარდიოლოგია"]


def test_tokenize_strips_admin_title_phrase():
    assert tokenize("არითმოლოგიის ცენტრის ხელმძღვანელი") == ["არითმოლოგიის"]


def test_tokenize_keeps_plain_specialty():
    assert tokenize("კარდიოლოგია") == ["კარდიოლოგია"]


def test_match_alias_returns_slug_with_score_one(matcher_db: str) -> None:
    aliases = {normalize_alias("ოჯახის ექიმი"): "cardiology"}
    matcher = SpecialtyMatcher(dsn=matcher_db, aliases=aliases)
    result = matcher.match(token_ka="ოჯახის ექიმი", token_en=None)
    assert result is not None
    assert result.slug == "cardiology"
    assert result.score == 1.0


def test_match_falls_through_to_fuzzy_when_not_aliased(matcher_db: str) -> None:
    matcher = SpecialtyMatcher(dsn=matcher_db, aliases={normalize_alias("ოჯახის ექიმი"): "cardiology"})
    result = matcher.match(token_ka="ნევროლოგია", token_en=None)
    assert result is not None and result.slug == "neurology"


def test_match_alias_to_unknown_slug_falls_through(matcher_db: str) -> None:
    matcher = SpecialtyMatcher(dsn=matcher_db, aliases={normalize_alias("ექოსკოპისტი"): "ultrasound-diagnostics"})
    # ultrasound-diagnostics is not seeded in matcher_db -> alias can't resolve -> None
    assert matcher.match(token_ka="ექოსკოპისტი", token_en=None) is None
