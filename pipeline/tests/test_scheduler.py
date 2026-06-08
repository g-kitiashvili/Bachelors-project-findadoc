from datetime import datetime

from pipeline.infra.scheduler import next_run_time


def test_next_run_time_after_03_00_in_tbilisi():
    now = datetime.fromisoformat("2026-05-23T04:00:00+04:00")
    nxt = next_run_time("0 3 * * *", "Asia/Tbilisi", now=now)
    assert nxt == datetime.fromisoformat("2026-05-24T03:00:00+04:00")


def test_next_run_time_before_03_00_in_tbilisi():
    now = datetime.fromisoformat("2026-05-23T02:00:00+04:00")
    nxt = next_run_time("0 3 * * *", "Asia/Tbilisi", now=now)
    assert nxt == datetime.fromisoformat("2026-05-23T03:00:00+04:00")
