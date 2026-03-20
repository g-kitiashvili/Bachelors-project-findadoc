# findadoc-pipeline

Python data-ingestion pipeline for Find-a-Doc.

## Sources

| Source | Domain | Fetcher | Status |
|---|---|---|---|
| newhospitals | newhospitals.ge | httpx | active (~191 doctors) |
| aversi | aversiclinic.ge | Playwright + stealth (CF bypass) | active (~480 doctors) |

## Two entrypoints

```bash
# One-shot run
python -m pipeline run --source newhospitals
python -m pipeline run --source aversi
python -m pipeline run --all

# Long-running scheduler (used by the docker-compose pipeline service)
python -m pipeline scheduler
```

Both call into the same scraper code; only the trigger differs.

## Local install

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m playwright install chromium
python -m pipeline run --source newhospitals
```

## Tests

```bash
# Fast tests only (default):
pytest

# Include slow tests (Testcontainers + Playwright integration):
pytest -m "slow or not slow"
```

## Configuration (env vars)

| Var | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | _required_ | Postgres DSN |
| `PIPELINE_RATE_PER_SEC` | `1.0` | Default fetcher rate cap |
| `PIPELINE_SCHEDULER_CRON` | `0 3 * * *` | Cron expression |
| `PIPELINE_TIMEZONE` | `Asia/Tbilisi` | Scheduler timezone |
| `PIPELINE_LOG_LEVEL` | `INFO` | structlog level |
| `PIPELINE_PLAYWRIGHT_HEADLESS` | `true` | Default; AversiScraper overrides to `false` |

## Aversi runtime note

Aversi sits behind Cloudflare bot protection. The only confirmed bypass is headed
Chromium + `playwright-stealth` + 8s post-navigation wait. In production, the pipeline
runs inside the Docker container based on `mcr.microsoft.com/playwright/python` —
Xvfb is preinstalled there, so the headed browser renders to a virtual framebuffer
(no visible window). When running directly on a local machine, a Chromium window
pops up briefly during scraping.

`AversiScraper.discover()` is capped at `max_pages=2` by default (~32 doctors).
For full coverage (~480 doctors across 30 pages), construct the scraper explicitly:

```python
from pipeline.scrapers.aversi import AversiScraper
AversiScraper(max_pages=30)
```

## Adding a new source

1. Capture HTML fixtures into `tests/fixtures/<source>/`.
2. Create `pipeline/scrapers/<source>.py` implementing the `Scraper` protocol.
3. Add a self-registration line: `register(<Source>Scraper())`.
4. Import in `pipeline/scrapers/__init__.py`.
5. Add fixture-driven tests.
