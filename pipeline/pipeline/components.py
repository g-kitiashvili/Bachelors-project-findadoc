"""Composition root: the single place pipeline objects are constructed and wired.

Both the standalone CLI commands and the Runner build their dependencies through a
`Components` instance, so each seeder / matcher / pass is created in exactly one
place (no more building the same object in a command branch and again in the runner
factory). Each method returns a fresh instance; callers use what they need.
"""

from __future__ import annotations

from pathlib import Path

from pipeline.config import Settings
from pipeline.domain.non_providers import NonProviderList
from pipeline.domain.taxonomy import build_alias_index, load_specialties
from pipeline.runner import Runner
from pipeline.services.brand_linker import BrandLinkingPass
from pipeline.services.clinic_pass import ClinicPass
from pipeline.services.deduplicator import Deduplicator
from pipeline.services.geocoder import GeocodeClinicsPass
from pipeline.services.location_matcher import LocationMatcher
from pipeline.services.location_seeder import LocationSeeder
from pipeline.services.medical_condition_seeder import MedicalConditionSeeder
from pipeline.services.pass_base import Pass
from pipeline.services.persister import Persister
from pipeline.services.prominence import ProminencePass
from pipeline.services.remapper import Remapper
from pipeline.services.seeder_base import Seeder
from pipeline.services.specialty_matcher import SpecialtyMatcher
from pipeline.services.specialty_seeder import SpecialtySeeder

_DATA = Path(__file__).parent / "data"
_SPECIALTY_YAML = _DATA / "specialties.yaml"
_LOCATION_YAML = _DATA / "locations.yaml"
_CONDITIONS_YAML = _DATA / "conditions.yaml"
_NON_PROVIDERS_YAML = _DATA / "non_providers.yaml"
_BRANDS_YAML = _DATA / "brands.yaml"
_SEARCH_KEYWORDS_YAML = _DATA / "search_keywords.yaml"


class Components:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._dsn = settings.database_url

    # --- matchers + write path ---
    def specialty_matcher(self) -> SpecialtyMatcher:
        aliases = build_alias_index(load_specialties(_SPECIALTY_YAML))
        return SpecialtyMatcher(dsn=self._dsn, aliases=aliases)

    def non_providers(self) -> NonProviderList:
        return NonProviderList.load(_NON_PROVIDERS_YAML)

    def persister(self) -> Persister:
        return Persister(
            self._dsn,
            specialty_matcher=self.specialty_matcher(),
            location_matcher=LocationMatcher(dsn=self._dsn),
            non_providers=self.non_providers(),
        )

    def remapper(self) -> Remapper:
        return Remapper(self._dsn, matcher=self.specialty_matcher(), non_providers=self.non_providers())

    # --- reference-data seeders (ordered: specialties before conditions) ---
    def specialty_seeder(self) -> SpecialtySeeder:
        return SpecialtySeeder(dsn=self._dsn, yaml_path=_SPECIALTY_YAML, keywords_path=_SEARCH_KEYWORDS_YAML)

    def location_seeder(self) -> LocationSeeder:
        return LocationSeeder(dsn=self._dsn, yaml_path=_LOCATION_YAML)

    def condition_seeder(self) -> MedicalConditionSeeder:
        return MedicalConditionSeeder(dsn=self._dsn, yaml_path=_CONDITIONS_YAML)

    def seeders(self) -> list[Seeder]:
        return [self.location_seeder(), self.specialty_seeder(), self.condition_seeder()]

    # --- post-scrape passes (ordered: dedup first) ---
    def deduplicator(self) -> Deduplicator:
        return Deduplicator(self._dsn)

    def geocoder(self) -> GeocodeClinicsPass:
        return GeocodeClinicsPass(self._dsn)

    def brand_linker(self) -> BrandLinkingPass:
        return BrandLinkingPass(dsn=self._dsn, yaml_path=_BRANDS_YAML)

    def prominence(self) -> ProminencePass:
        return ProminencePass(self._dsn)

    def clinic_pass(self) -> ClinicPass:
        return ClinicPass(self._dsn)

    def post_passes(self) -> list[Pass]:
        return [self.deduplicator(), self.geocoder(), self.brand_linker(), self.prominence()]

    # --- orchestration ---
    def runner(self) -> Runner:
        return Runner(
            persister=self.persister(),
            seeders=self.seeders(),
            post_passes=self.post_passes(),
            persister_factory=self.persister,  # a fresh persister per parallel worker
            scrape_workers=self.settings.pipeline_scrape_workers,
        )
