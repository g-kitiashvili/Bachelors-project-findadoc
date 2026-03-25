"""CLI dispatch — argparse-based.

Subcommands:
  run --source X      → run one scraper and exit
  run --all           → run every registered scraper and exit
  scheduler           → long-running APScheduler loop
  seed-specialties    → upsert the specialty taxonomy from YAML and exit
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import structlog

from pipeline.config import Settings
from pipeline.core.persister import Persister
from pipeline.core.runner import Runner
from pipeline.core.scheduler import run_blocking_scheduler
from pipeline.core.specialty_matcher import SpecialtyMatcher
from pipeline.core.specialty_seeder import SpecialtySeeder


_SPECIALTY_YAML_PATH = Path(__file__).parent / "data" / "specialties.yaml"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pipeline", description="Find-a-Doc data pipeline")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="One-shot run; exits when done.")
    group = p_run.add_mutually_exclusive_group(required=True)
    group.add_argument("--source", help="Run a single scraper by name.")
    group.add_argument("--all", action="store_true", help="Run every registered scraper.")

    sub.add_parser("scheduler", help="Long-running scheduler loop.")
    sub.add_parser("seed-specialties", help="Upsert the specialty taxonomy from YAML.")
    return parser


def _configure_logging(level: str) -> None:
    logging.basicConfig(level=level.upper(), format="%(message)s")
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ]
    )


def _make_runner(settings: Settings) -> Runner:
    matcher = SpecialtyMatcher(dsn=settings.database_url)
    persister = Persister(settings.database_url, specialty_matcher=matcher)
    seeder = SpecialtySeeder(dsn=settings.database_url, yaml_path=_SPECIALTY_YAML_PATH)
    return Runner(persister=persister, specialty_seeder=seeder)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = Settings()
    _configure_logging(settings.pipeline_log_level)

    # Importing pipeline.scrapers registers all known scrapers via side-effect.
    import pipeline.scrapers  # noqa: F401

    if args.cmd == "seed-specialties":
        SpecialtySeeder(dsn=settings.database_url, yaml_path=_SPECIALTY_YAML_PATH).seed()
        return 0

    runner = _make_runner(settings)

    if args.cmd == "run":
        if args.source:
            runner.run_source(args.source)
        else:
            runner.run_all()
        return 0

    if args.cmd == "scheduler":
        run_blocking_scheduler(
            runner,
            cron_expr=settings.pipeline_scheduler_cron,
            tz_name=settings.pipeline_timezone,
        )
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
