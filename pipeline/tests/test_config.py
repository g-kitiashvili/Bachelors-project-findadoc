import pytest
from pipeline.config import Settings


def test_default_settings_pick_up_database_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h:5432/d")
    s = Settings()
    assert str(s.database_url) == "postgresql://u:p@h:5432/d"
    assert s.pipeline_rate_per_sec == 1.0
    assert s.pipeline_scheduler_cron == "0 3 * * *"
    assert s.pipeline_timezone == "Asia/Tbilisi"
    assert s.pipeline_log_level == "INFO"
    assert s.pipeline_playwright_headless is True


def test_settings_missing_database_url_raises(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValueError):
        Settings()


def test_settings_overrides_via_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h:5432/d")
    monkeypatch.setenv("PIPELINE_RATE_PER_SEC", "0.25")
    monkeypatch.setenv("PIPELINE_PLAYWRIGHT_HEADLESS", "false")
    s = Settings()
    assert s.pipeline_rate_per_sec == 0.25
    assert s.pipeline_playwright_headless is False
