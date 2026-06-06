"""Process-wide configuration for the pipeline."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, case_sensitive=False, extra="ignore")

    database_url: str = Field(..., description="Postgres DSN, e.g. postgresql://user:pw@host:5432/db")
    pipeline_rate_per_sec: float = 1.0
    pipeline_scheduler_cron: str = "0 3 * * *"
    pipeline_timezone: str = "Asia/Tbilisi"
    pipeline_log_level: str = "INFO"
    # Sources scraped concurrently in `run --all`. 0 = one thread per source (all at
    # once, the default - each source hits a different site); 1 = sequential; N = cap at N.
    pipeline_scrape_workers: int = 0
