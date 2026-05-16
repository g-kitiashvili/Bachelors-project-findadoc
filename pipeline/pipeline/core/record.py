"""Domain record produced by scrapers and consumed by the persister."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ClinicRef(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    source_url: HttpUrl
    name_ka: str = Field(..., min_length=1)
    name_en: str | None = None
    address: str | None = None
    phone: str | None = None
    website: HttpUrl | None = None


class DoctorRecord(BaseModel):
    """One doctor as observed from a single source page.

    Scraper-produced fields may have `full_name_en` and `slug_base` as None.
    `translit.normalize` fills both before the persister sees the record.
    """

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    source: str = Field(..., min_length=1, description="Source name, e.g. 'aversi'")
    source_url: HttpUrl
    full_name_ka: str = Field(..., min_length=1)
    full_name_en: str | None = None
    photo_url: HttpUrl | None = None
    bio_ka: str | None = None
    bio_en: str | None = None
    gender: Literal["male", "female", "other"] | None = None
    specialty_ka: str | None = None
    specialty_en: str | None = None
    slug_base: str | None = None
    city: str | None = None
    clinics: tuple[ClinicRef, ...] = ()
