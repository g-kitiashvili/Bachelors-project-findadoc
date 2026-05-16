"""evex.ge scraper — Georgian hospital chain (Laravel JSON API), via httpx."""

from __future__ import annotations

import json
from collections.abc import Iterator

from pipeline.core.fetcher import HttpxFetcher
from pipeline.core.record import ClinicRef, DoctorRecord
from pipeline.core.registry import register
from pipeline.core.translit import english_or_none


_API = "https://admin.evex.ge/api"
_LIST_URL = f"{_API}/archives/chveni-ekimebi"
_PROFILE_BASE = "https://evex.ge/ka/archive/chveni-ekimebi"


def _slug(obj: dict) -> str | None:
    slug = obj.get("slug")
    if isinstance(slug, dict):
        return slug.get("ka") or slug.get("en")
    return slug


def _clinics(doctor: dict) -> tuple[ClinicRef, ...]:
    clinics: list[ClinicRef] = []
    seen: set[str] = set()
    for c in doctor.get("clinics") or []:
        name = ((c.get("title") or {}).get("ka") or "").strip()
        clinic_id = c.get("id")
        if not name or clinic_id is None:
            continue
        source_url = f"{_API}/clinics/{clinic_id}"
        if source_url in seen:
            continue
        seen.add(source_url)
        address = ((c.get("address") or {}).get("ka") or "").strip() or None
        phone = (c.get("phone") or "").strip() or None
        name_en = english_or_none((c.get("title") or {}).get("en"))
        clinics.append(ClinicRef(source_url=source_url, name_ka=name, name_en=name_en, address=address, phone=phone))
    return tuple(clinics)


def _to_record(doctor: dict) -> DoctorRecord | None:
    name_ka = ((doctor.get("name") or {}).get("ka") or "").strip()
    slug = _slug(doctor)
    if not name_ka or not slug:
        return None
    return DoctorRecord(
        source="evex",
        source_url=f"{_PROFILE_BASE}/{slug}",
        full_name_ka=name_ka,
        full_name_en=english_or_none((doctor.get("name") or {}).get("en")),
        specialty_ka=((doctor.get("title") or {}).get("ka") or "").strip() or None,
        specialty_en=english_or_none((doctor.get("title") or {}).get("en")),
        photo_url=doctor.get("image") or None,
        city=((doctor.get("city") or {}).get("name") or {}).get("ka") or None,
        clinics=_clinics(doctor),
    )


class EvexScraper:
    name = "evex"

    def __init__(self, fetcher=None) -> None:
        self.fetcher = fetcher or HttpxFetcher(rate_per_sec=2.0)

    def discover(self) -> Iterator[str]:
        seen: set[str] = set()
        page = 1
        while True:
            payload = (json.loads(self.fetcher.get(f"{_LIST_URL}?page={page}")) or {}).get("data") or {}
            items = payload.get("items") or []
            if not items:
                break
            for item in items:
                slug = _slug(item)
                if not slug:
                    continue
                url = f"{_API}/doctors/{slug}"
                if url not in seen:
                    seen.add(url)
                    yield url
            last = (payload.get("pagination") or {}).get("last_page")
            if last is not None and page >= int(last):
                break
            page += 1

    def extract(self, html: str, url: str) -> DoctorRecord | None:
        try:
            data = json.loads(html)
        except json.JSONDecodeError:
            return None
        doctor = data.get("data") if isinstance(data, dict) else None
        if not isinstance(doctor, dict):
            return None
        return _to_record(doctor)


register(EvexScraper())
