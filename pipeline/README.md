# findadoc-pipeline

Python data-ingestion pipeline for Find-a-Doc.

## Two entrypoints

```bash
# One-shot run (used by ad-hoc invocations and scheduled CI jobs)
python -m pipeline run --source aversi
python -m pipeline run --all

# Long-running scheduler (used by the docker-compose `pipeline` service)
python -m pipeline scheduler
```

Both call into the same scraper code; only the trigger differs.

## Local install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pipeline run --all
```

## Tests

```bash
pytest
```
