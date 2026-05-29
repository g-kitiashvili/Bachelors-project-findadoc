import type { PageServerLoad } from "./$types";
import type { SpecialtyRef, ClinicRef, LocationRegion } from "../+page.server";

const API_BASE = process.env.API_URL ?? "http://localhost:8080";

interface Pin { slug: string; nameEn: string; nameKa: string; lat: number; lng: number; doctorCount: number }

export const load: PageServerLoad = async ({ url, fetch }) => {
  const q = (url.searchParams.get("q") ?? "").trim();
  const specialty = (url.searchParams.get("specialty") ?? "").trim();
  const region = (url.searchParams.get("region") ?? "").trim();
  const city = (url.searchParams.get("city") ?? "").trim();
  const clinic = (url.searchParams.get("clinic") ?? "").trim();
  const condition = (url.searchParams.get("condition") ?? "").trim();

  // Pins for the active filter set (same filters as the doctor list).
  const pinParams = new URLSearchParams();
  for (const [k, v] of [["q", q], ["specialty", specialty], ["region", region], ["city", city], ["clinic", clinic], ["condition", condition]]) {
    if (v) pinParams.set(k, v);
  }
  const center = url.searchParams.get("center");
  const radiusKm = url.searchParams.get("radius_km");
  if (center) pinParams.set("center", center);
  if (radiusKm) pinParams.set("radius_km", radiusKm);
  const pinQs = pinParams.toString();
  const pinsRes = await fetch(`${API_BASE}/api/v1/doctors/map-pins${pinQs ? `?${pinQs}` : ""}`);
  const pins: Pin[] = pinsRes.ok ? ((await pinsRes.json()) as { pins: Pin[] }).pins : [];

  // Filter-control data, mirroring the doctor list page so the same FilterBar works here.
  const specParams = new URLSearchParams();
  if (region) specParams.set("region", region);
  if (city) specParams.set("city", city);
  if (clinic) specParams.set("clinic", clinic);
  const specRes = await fetch(`${API_BASE}/api/v1/specialties${specParams.toString() ? `?${specParams}` : ""}`);
  const specialties = (specRes.ok ? ((await specRes.json()) as { items: Array<SpecialtyRef & { doctorCount: number; parentSlug?: string | null }> }).items : [])
    .filter((s) => s.doctorCount > 0);

  const locParams = new URLSearchParams();
  if (specialty) locParams.set("specialty", specialty);
  if (clinic) locParams.set("clinic", clinic);
  const locRes = await fetch(`${API_BASE}/api/v1/locations${locParams.toString() ? `?${locParams}` : ""}`);
  const regions = locRes.ok ? ((await locRes.json()) as { items: LocationRegion[] }).items : [];

  const clinicParams = new URLSearchParams({ located: "true" }); // the map only filters by clinics it can place
  if (region) clinicParams.set("region", region);
  if (city) clinicParams.set("city", city);
  if (specialty) clinicParams.set("specialty", specialty);
  const clinicsRes = await fetch(`${API_BASE}/api/v1/clinics?${clinicParams}`);
  const clinics = clinicsRes.ok ? ((await clinicsRes.json()) as { items: ClinicRef[] }).items : [];

  const parts = center?.split(",").map((s) => Number(s.trim()));
  const centerPoint = parts && parts.length === 2 && parts.every(Number.isFinite) ? { lat: parts[0], lng: parts[1] } : null;
  const radius = Number(radiusKm);

  return {
    pins,
    centerPoint,
    focus: url.searchParams.get("focus"),
    isMyLocation: url.searchParams.get("me") === "1",
    radiusKm: Number.isFinite(radius) && radius > 0 ? radius : null,
    q,
    query: url.search,
    specialties,
    regions,
    clinics,
    selectedSlugs: specialty ? specialty.split(",").filter(Boolean) : [],
    selectedRegion: region,
    selectedCity: city,
    selectedClinics: clinic ? clinic.split(",").filter(Boolean) : [],
  };
};
