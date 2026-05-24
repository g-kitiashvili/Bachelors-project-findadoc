"""aversiclinic.ge scraper — public dashboard JSON API, via httpx.

The aversiclinic.ge SPA sits behind Cloudflare, but its data is served by an
unprotected dashboard REST API: `https://dashboard.aversiclinic.ge/api/doctors/{lang}`
(`lang` in {ka, en}). We pair the ka and en pages by doctor id; en names are Latin
for ~64% of doctors (the rest stay Georgian-script → english_or_none drops them and
the runner's romanization fills full_name_en).

The API has no per-doctor detail endpoint and ignores `per_page` (always 16 per page).
Since the Runner fetches each url discover() yields and hands the same url to extract(),
discover() paginates ka+en once into memory and yields one url per doctor carrying the
doctor id in an `_id` query param the server ignores; extract() reads `_id` to pick the
doctor from the fetched page and pairs it with the cached en page.
"""

from __future__ import annotations

import json
from collections.abc import Iterator

from pipeline.core.clinic_normalize import brand_prefixed, strip_sublabel
from pipeline.core.fetcher import FetchError, HttpxFetcher
from pipeline.core.record import ClinicRef, DoctorRecord
from pipeline.core.registry import register
from pipeline.core.translit import english_or_none


_BRAND_KA = "ავერსი"
_BRAND_EN = "Aversi"


_DASHBOARD = "https://dashboard.aversiclinic.ge"
_API = f"{_DASHBOARD}/api/doctors"
_PHOTO_BASE = f"{_DASHBOARD}/storage"
_PROFILE_BASE = "https://aversiclinic.ge/doctors/doctor"
_BRANCH_BASE = f"{_DASHBOARD}/branch"

_BRAND_CLINIC = ClinicRef(
    source_url="https://aversiclinic.ge",
    name_ka="ავერსის კლინიკა",
    name_en="Aversi Clinic",
)


def _first_specialty(doctor: dict) -> str | None:
    for spec in doctor.get("specialties") or []:
        title = (spec.get("title") or "").strip()
        if title:
            return title
    return None


def _photo_url(doctor: dict) -> str | None:
    photo = (doctor.get("photo") or "").strip()
    if not photo:
        return None
    return f"{_PHOTO_BASE}/{photo.lstrip('/')}"


def _clinics(ka_doctor: dict, en_doctor: dict | None) -> tuple[ClinicRef, ...]:
    en_by_id = {b.get("id"): b for b in (en_doctor or {}).get("branches") or []}
    clinics: list[ClinicRef] = []
    seen: set[int] = set()
    for branch in ka_doctor.get("branches") or []:
        branch_id = branch.get("id")
        name_ka = (branch.get("title") or "").strip()
        if branch_id is None or not name_ka or branch_id in seen:
            continue
        seen.add(branch_id)
        en_branch = en_by_id.get(branch_id) or {}
        en_title = english_or_none(en_branch.get("title"))
        clinics.append(
            ClinicRef(
                source_url=f"{_BRANCH_BASE}/{branch_id}",
                name_ka=brand_prefixed(strip_sublabel(name_ka), _BRAND_KA),
                name_en=brand_prefixed(strip_sublabel(en_title), _BRAND_EN) if en_title else None,
                address=(branch.get("address") or "").strip() or None,
            )
        )
    return tuple(clinics) if clinics else (_BRAND_CLINIC,)


def _to_record(ka_doctor: dict, en_doctor: dict | None) -> DoctorRecord | None:
    doctor_id = ka_doctor.get("id")
    name_ka = (ka_doctor.get("name") or "").strip()
    if doctor_id is None or not name_ka:
        return None
    en = en_doctor or {}
    return DoctorRecord(
        source="aversi",
        source_url=f"{_PROFILE_BASE}/{doctor_id}",
        full_name_ka=name_ka,
        full_name_en=english_or_none(en.get("name")),
        photo_url=_photo_url(ka_doctor),
        gender=ka_doctor.get("gender") if ka_doctor.get("gender") in ("male", "female", "other") else None,
        specialty_ka=_first_specialty(ka_doctor),
        specialty_en=english_or_none(_first_specialty(en)),
        clinics=_clinics(ka_doctor, en_doctor),
    )


def _doctor_id_from_url(url: str) -> int | None:
    from urllib.parse import parse_qs, urlsplit

    values = parse_qs(urlsplit(url).query).get("_id")
    if not values:
        return None
    try:
        return int(values[0])
    except ValueError:
        return None


class AversiScraper:
    name = "aversi"

    def __init__(self, fetcher=None, *, max_pages: int = 30) -> None:
        self.fetcher = fetcher or HttpxFetcher(rate_per_sec=2.0)
        self._max_pages = max_pages
        self._en_by_id: dict[int, dict] = {}

    def _page(self, lang: str, page: int) -> list[dict]:
        try:
            payload = json.loads(self.fetcher.get(f"{_API}/{lang}?page={page}"))
        except (FetchError, json.JSONDecodeError):
            return []
        data = payload.get("data") if isinstance(payload, dict) else None
        return data if isinstance(data, list) else []

    def discover(self) -> Iterator[str]:
        self._en_by_id = {}
        seen: set[int] = set()
        for page in range(1, self._max_pages + 1):
            ka_docs = self._page("ka", page)
            if not ka_docs:
                break
            for en_doc in self._page("en", page):
                en_id = en_doc.get("id")
                if en_id is not None:
                    self._en_by_id[en_id] = en_doc
            for ka_doc in ka_docs:
                doctor_id = ka_doc.get("id")
                if doctor_id is None or doctor_id in seen:
                    continue
                seen.add(doctor_id)
                yield f"{_API}/ka?page={page}&_id={doctor_id}"

    def extract(self, html: str, url: str) -> DoctorRecord | None:
        try:
            payload = json.loads(html)
        except json.JSONDecodeError:
            return None
        data = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(data, list):
            return None
        doctor_id = _doctor_id_from_url(url)
        ka_doctor = next((d for d in data if d.get("id") == doctor_id), None)
        if ka_doctor is None:
            return None
        return _to_record(ka_doctor, self._en_by_id.get(doctor_id))


register(AversiScraper())
