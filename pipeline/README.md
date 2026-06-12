# findadoc-pipeline

Python data-ingestion pipeline for Find-a-Doc.

## Sources

All sources are fetched with `httpx` over static HTML or JSON; no headless browser is used.

| Source | Domain | Notes |
|---|---|---|
| newhospitals | newhospitals.ge | static HTML |
| aversi | aversiclinic.ge | public dashboard JSON API (`dashboard.aversiclinic.ge/api/doctors/{lang}`) |
| caraps | carapsmedline.ge | static HTML |
| cmc | cmchospital.ge | static HTML, EN + KA pages |
| evex | evex.ge | JSON API, bilingual |
| joann | joann.ge | static HTML |
| tsamali | tsamali.ge | static HTML, per-city listings |
| vipmed | vipmed.ge | static HTML |
| vivamedi | vivamedi.ge | static HTML |
| vivomedical | vivomedical.ge | static HTML |

A full run ingests roughly 3,200 doctors across all sources.

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
python -m pipeline run --source newhospitals
```

## Tests

```bash
# Fast tests only (default):
pytest

# Include slow tests (Testcontainers integration):
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

## Adding a new source

1. Capture HTML fixtures into `tests/fixtures/<source>/`.
2. Create `pipeline/scrapers/<source>.py` implementing the `Scraper` protocol.
3. Add a self-registration line: `register(<Source>Scraper())`.
4. Import in `pipeline/scrapers/__init__.py`.
5. Add fixture-driven tests.
