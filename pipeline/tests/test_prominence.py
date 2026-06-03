from __future__ import annotations

from pipeline.core.prominence import _host, prominence_score


def _full(**over):
    base = dict(sources=4, has_photo=True, has_bio=True, specialties=3, clinics=2, days_since_update=0.0)
    base.update(over)
    return prominence_score(**base)


def test_max_score_is_100():
    assert _full() == 100.0


def test_min_score_is_0():
    assert prominence_score(
        sources=1, has_photo=False, has_bio=False, specialties=0, clinics=0, days_since_update=400.0
    ) == 0.0


def test_corroboration_is_capped_and_weighted_040():
    # one extra source past 4 adds nothing; from 1 source to 4+ is the full 40 points
    one = prominence_score(sources=1, has_photo=False, has_bio=False, specialties=0, clinics=0, days_since_update=None)
    four = prominence_score(sources=4, has_photo=False, has_bio=False, specialties=0, clinics=0, days_since_update=None)
    ten = prominence_score(sources=10, has_photo=False, has_bio=False, specialties=0, clinics=0, days_since_update=None)
    assert one == 0.0
    assert four == 40.0
    assert ten == four


def test_completeness_each_half_worth_half_of_025():
    photo_only = prominence_score(sources=1, has_photo=True, has_bio=False, specialties=0, clinics=0, days_since_update=None)
    both = prominence_score(sources=1, has_photo=True, has_bio=True, specialties=0, clinics=0, days_since_update=None)
    assert photo_only == 12.5
    assert both == 25.0


def test_recency_decays_linearly_over_a_year():
    fresh = prominence_score(sources=1, has_photo=False, has_bio=False, specialties=0, clinics=0, days_since_update=0.0)
    half = prominence_score(sources=1, has_photo=False, has_bio=False, specialties=0, clinics=0, days_since_update=182.5)
    stale = prominence_score(sources=1, has_photo=False, has_bio=False, specialties=0, clinics=0, days_since_update=400.0)
    assert fresh == 15.0
    assert round(half, 1) == 7.5
    assert stale == 0.0


def test_missing_update_timestamp_scores_zero_recency():
    assert prominence_score(
        sources=1, has_photo=False, has_bio=False, specialties=0, clinics=0, days_since_update=None
    ) == 0.0


def test_host_strips_scheme_and_www():
    assert _host("https://www.vivamedi.ge/doctor?doctor_id=20") == "vivamedi.ge"
    assert _host("http://tsamali.ge/x") == "tsamali.ge"
    assert _host(None) == ""
