"""One-off normalization of already-persisted clinic rows (mirror of Remapper).

Re-applies the scrape-time clinic rules to existing rows so a full re-scrape isn't
needed: brand-prefixes Aversi branches, deactivates aggregator role/affiliation
phrases that aren't real clinics, and fills the romanized address_en. Run the
`dedup` pass afterwards to merge the cross-source duplicates this leaves in place.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlsplit

import psycopg
import structlog

from pipeline.core.clinic_normalize import brand_prefixed, is_role_phrase, strip_sublabel
from pipeline.core.translit import address_to_en

log = structlog.get_logger("pipeline.clinic_pass")

_AGGREGATOR_HOSTS = frozenset({"tsamali.ge", "vipmed.ge"})
_BRAND_KA = "ავერსი"
_BRAND_EN = "Aversi"


@dataclass(frozen=True)
class ClinicPassStats:
    total: int
    deactivated: int
    renamed: int
    addressed: int


class ClinicNormalizePass:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def run(self) -> ClinicPassStats:
        with psycopg.connect(self._dsn, autocommit=True) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT id, name_ka, name_en, address, address_en, last_source_url "
                "FROM clinic WHERE status='ACTIVE'"
            )
            rows = cur.fetchall()
            deactivated = renamed = addressed = 0
            for cid, name_ka, name_en, address, address_en, url in rows:
                host = urlsplit(url or "").netloc
                if host in _AGGREGATOR_HOSTS and is_role_phrase(name_en, name_ka):
                    cur.execute("UPDATE clinic SET status='INACTIVE' WHERE id=%s", (cid,))
                    deactivated += 1
                    continue
                new_ka, new_en = name_ka, name_en
                if "aversiclinic.ge" in host or host == "aversi.ge":
                    new_ka = brand_prefixed(strip_sublabel(name_ka), _BRAND_KA)
                    new_en = brand_prefixed(strip_sublabel(name_en), _BRAND_EN) if name_en else name_en
                new_address_en = address_to_en(address)
                if (new_ka, new_en, new_address_en) != (name_ka, name_en, address_en):
                    cur.execute(
                        "UPDATE clinic SET name_ka=%s, name_en=%s, address_en=%s WHERE id=%s",
                        (new_ka, new_en, new_address_en, cid),
                    )
                    if (new_ka, new_en) != (name_ka, name_en):
                        renamed += 1
                    if new_address_en != address_en:
                        addressed += 1
            stats = ClinicPassStats(len(rows), deactivated, renamed, addressed)
            log.info("clinic_normalize_complete", **stats.__dict__)
            return stats
