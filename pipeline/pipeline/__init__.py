"""Find-a-Doc data pipeline.

Scrapes Georgian clinic websites and PDF directories, normalizes the records,
and writes them into the Find-a-Doc Postgres database.

Two entrypoints:
- `python -m pipeline run [--source X | --all]` — one-shot run, exits when done.
  Used for ad-hoc invocation and (in production) the GitHub Actions cron.
- `python -m pipeline scheduler` — long-running APScheduler loop.
  Used by the docker-compose `pipeline` service.
"""

__version__ = "0.1.0"
