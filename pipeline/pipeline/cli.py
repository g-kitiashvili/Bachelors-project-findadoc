"""CLI: argparse parsing + a command dispatch table.

Each subcommand maps to a handler `(components, args) -> int`. All object
construction lives in `Components` (the composition root), so this module only
parses arguments and dispatches.
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Callable

import structlog

from pipeline.components import Components
from pipeline.config import Settings
from pipeline.infra.scheduler import run_blocking_scheduler
from pipeline.services.remapper import RemapRegression


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pipeline", description="Find-a-Doc data pipeline")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="One-shot run; exits when done.")
    group = p_run.add_mutually_exclusive_group(required=True)
    group.add_argument("--source", help="Run a single scraper by name.")
    group.add_argument("--all", action="store_true", help="Run every registered scraper.")

    sub.add_parser("scheduler", help="Long-running scheduler loop.")
    sub.add_parser("seed-specialties", help="Upsert the specialty taxonomy from YAML.")
    sub.add_parser("seed-locations", help="Upsert the region/city taxonomy from YAML.")
    sub.add_parser("seed-conditions", help="Upsert medical conditions from YAML (run after seed-specialties).")
    sub.add_parser("remap-specialties", help="Re-map all doctors' specialties from stored data.")
    sub.add_parser("dedup", help="Merge cross-source duplicate doctors and clinics.")
    sub.add_parser("normalize-clinics", help="Normalize existing clinic rows (names, junk, address_en).")
    sub.add_parser("geocode-clinics", help="Geocode clinic addresses to coordinates via Nominatim.")
    sub.add_parser("link-brands", help="Link clinics to curated brands by name (run after dedup).")
    sub.add_parser("prominence", help="Recompute doctor prominence scores (run after dedup).")
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


def _cmd_run(c: Components, args: argparse.Namespace) -> int:
    runner = c.runner()
    if args.source:
        runner.run_source(args.source)
    else:
        runner.run_all()
    return 0


def _cmd_scheduler(c: Components, args: argparse.Namespace) -> int:
    run_blocking_scheduler(
        c.runner(),
        cron_expr=c.settings.pipeline_scheduler_cron,
        tz_name=c.settings.pipeline_timezone,
    )
    return 0


def _cmd_remap(c: Components, args: argparse.Namespace) -> int:
    c.specialty_seeder().seed()  # remap against the current taxonomy
    try:
        c.remapper().remap_all()
    except RemapRegression:
        return 1
    return 0


def _ok(action: Callable[[Components], object]) -> Callable[[Components, argparse.Namespace], int]:
    """Wrap a fire-and-forget action into a handler that runs it and returns exit code 0."""
    def handler(c: Components, args: argparse.Namespace) -> int:
        action(c)
        return 0
    return handler


# command name -> handler(components, args) -> exit code
_COMMANDS: dict[str, Callable[[Components, argparse.Namespace], int]] = {
    "run": _cmd_run,
    "scheduler": _cmd_scheduler,
    "remap-specialties": _cmd_remap,
    "seed-specialties": _ok(lambda c: c.specialty_seeder().seed()),
    "seed-locations": _ok(lambda c: c.location_seeder().seed()),
    "seed-conditions": _ok(lambda c: c.condition_seeder().seed()),
    "dedup": _ok(lambda c: c.deduplicator().run()),
    "normalize-clinics": _ok(lambda c: c.clinic_pass().run()),
    "geocode-clinics": _ok(lambda c: c.geocoder().run()),
    "link-brands": _ok(lambda c: c.brand_linker().run()),
    "prominence": _ok(lambda c: c.prominence().run()),
}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = Settings()
    _configure_logging(settings.pipeline_log_level)

    # Importing pipeline.scrapers registers all known scrapers via side-effect.
    import pipeline.scrapers

    return _COMMANDS[args.cmd](Components(settings), args)


if __name__ == "__main__":
    sys.exit(main())
