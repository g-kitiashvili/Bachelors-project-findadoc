"""CLI dispatch — argparse-based.

Subcommands:
  run --source X      → run one scraper and exit
  run --all           → run every registered scraper and exit
  scheduler           → long-running APScheduler loop
  seed-specialties    → upsert the specialty taxonomy from YAML and exit
  seed-locations      → upsert the region/city taxonomy from YAML and exit
  seed-conditions     → upsert medical conditions from YAML (run after seed-specialties) and exit
  remap-specialties   → re-map every doctor's specialties from stored data and exit
  dedup               → merge cross-source duplicate doctors and clinics and exit
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import structlog

from pipeline.config import Settings
from pipeline.core.clinic_pass import ClinicNormalizePass
from pipeline.core.deduplicator import Deduplicator
from pipeline.core.geocoder import GeocodeClinicsPass
from pipeline.core.location_matcher import LocationMatcher
from pipeline.core.location_seeder import LocationSeeder
from pipeline.core.non_providers import NonProviderList
from pipeline.core.persister import Persister
from pipeline.core.remapper import RemapRegression, Remapper
from pipeline.core.runner import Runner
from pipeline.core.scheduler import run_blocking_scheduler
from pipeline.core.specialty_matcher import SpecialtyMatcher
from pipeline.core.medical_condition_seeder import MedicalConditionSeeder
from pipeline.core.specialty_seeder import SpecialtySeeder
from pipeline.core.brand_linker import BrandLinkingPass
from pipeline.core.taxonomy import build_alias_index, load_specialties

log = structlog.get_logger("pipeline.cli")

_SPECIALTY_YAML_PATH = Path(__file__).parent / "data" / "specialties.yaml"
_LOCATION_YAML_PATH = Path(__file__).parent / "data" / "locations.yaml"
_CONDITIONS_YAML_PATH = Path(__file__).parent / "data" / "conditions.yaml"
_NON_PROVIDERS_YAML_PATH = Path(__file__).parent / "data" / "non_providers.yaml"
_BRANDS_YAML_PATH = Path(__file__).parent / "data" / "brands.yaml"
_SEARCH_KEYWORDS_YAML_PATH = Path(__file__).parent / "data" / "search_keywords.yaml"


def _build_matcher(database_url: str) -> SpecialtyMatcher:
    aliases = build_alias_index(load_specialties(_SPECIALTY_YAML_PATH))
    return SpecialtyMatcher(dsn=database_url, aliases=aliases)


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
    matcher = _build_matcher(settings.database_url)
    location_matcher = LocationMatcher(dsn=settings.database_url)
    persister = Persister(
        settings.database_url,
        specialty_matcher=matcher,
        location_matcher=location_matcher,
        non_providers=NonProviderList.load(_NON_PROVIDERS_YAML_PATH),
    )
    specialty_seeder = SpecialtySeeder(dsn=settings.database_url, yaml_path=_SPECIALTY_YAML_PATH, keywords_path=_SEARCH_KEYWORDS_YAML_PATH)
    location_seeder = LocationSeeder(dsn=settings.database_url, yaml_path=_LOCATION_YAML_PATH)
    return Runner(
        persister=persister,
        specialty_seeder=specialty_seeder,
        location_seeder=location_seeder,
        deduplicator=Deduplicator(settings.database_url),
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = Settings()
    _configure_logging(settings.pipeline_log_level)

    # Importing pipeline.scrapers registers all known scrapers via side-effect.
    import pipeline.scrapers  # noqa: F401

    if args.cmd == "seed-specialties":
        SpecialtySeeder(dsn=settings.database_url, yaml_path=_SPECIALTY_YAML_PATH, keywords_path=_SEARCH_KEYWORDS_YAML_PATH).seed()
        return 0

    if args.cmd == "seed-locations":
        LocationSeeder(dsn=settings.database_url, yaml_path=_LOCATION_YAML_PATH).seed()
        return 0

    if args.cmd == "seed-conditions":
        MedicalConditionSeeder(dsn=settings.database_url, yaml_path=_CONDITIONS_YAML_PATH).seed()
        return 0

    if args.cmd == "remap-specialties":
        SpecialtySeeder(dsn=settings.database_url, yaml_path=_SPECIALTY_YAML_PATH, keywords_path=_SEARCH_KEYWORDS_YAML_PATH).seed()
        matcher = _build_matcher(settings.database_url)
        non_providers = NonProviderList.load(_NON_PROVIDERS_YAML_PATH)
        try:
            Remapper(settings.database_url, matcher=matcher, non_providers=non_providers).remap_all()
        except RemapRegression:
            return 1
        return 0

    if args.cmd == "dedup":
        Deduplicator(settings.database_url).run()
        return 0

    if args.cmd == "normalize-clinics":
        ClinicNormalizePass(settings.database_url).run()
        return 0

    if args.cmd == "geocode-clinics":
        GeocodeClinicsPass(settings.database_url).run()
        return 0

    if args.cmd == "link-brands":
        BrandLinkingPass(dsn=settings.database_url, yaml_path=_BRANDS_YAML_PATH).run()
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
