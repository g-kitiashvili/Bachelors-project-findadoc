import type { PageServerLoad } from "./$types";
import type { SpecialtyRef, ClinicRef, LocationRegion } from "../+page.server";
import { appendList } from "$lib/listParams";

const API_BASE = process.env.API_URL ?? "http://localhost:8080";

interface Pin { slug: string; nameEn: string; nameKa: string; lat: number; lng: number; doctorCount: number }

export const load: PageServerLoad = async ({ url, fetch }) => {
  const q = (url.searchParams.get("q") ?? "").trim();
  const specialty = (url.searchParams.get("specialty") ?? "").trim();
  const region = (url.searchParams.get("region") ?? "").trim();
  const city = (url.searchParams.get("city") ?? "").trim();
  const clinic = (url.searchParams.get("clinic") ?? "").trim();
  const condition = (url.searchParams.get("condition") ?? "").trim();
  const treatsChildren = url.searchParams.get("treatsChildren") === "true";
  const treatsAdults = url.searchParams.get("treatsAdults") === "true";

  // Pins for the active filter set (same filters as the doctor list).
  const pinParams = new URLSearchParams();
  for (const [k, v] of [["q", q], ["region", region], ["city", city]]) {
    if (v) pinParams.set(k, v);
  }
  appendList(pinParams, "specialty", specialty);
  appendList(pinParams, "clinic", clinic);
  appendList(pinParams, "condition", condition);
  if (treatsChildren) pinParams.set("treatsChildren", "true");
  if (treatsAdults) pinParams.set("treatsAdults", "true");
  const center = url.searchParams.get("center");
  const radiusKm = url.searchParams.get("radiusKm");
  if (center) pinParams.set("center", center);
  if (radiusKm) pinParams.set("radiusKm", radiusKm);
  const pinQs = pinParams.toString();
  const pinsRes = await fetch(`${API_BASE}/api/v1/doctors/map-pins${pinQs ? `?${pinQs}` : ""}`);
  const pins: Pin[] = pinsRes.ok ? ((await pinsRes.json()) as { pins: Pin[] }).pins : [];

  // Filter-control data, mirroring the doctor list page so the same FilterBar works here.
  const specParams = new URLSearchParams();
  if (region) specParams.set("region", region);
  if (city) specParams.set("city", city);
  appendList(specParams, "clinic", clinic);
  if (treatsChildren) specParams.set("treatsChildren", "true");
  if (treatsAdults) specParams.set("treatsAdults", "true");
  const specRes = await fetch(`${API_BASE}/api/v1/specialties${specParams.toString() ? `?${specParams}` : ""}`);
  const specialties = (specRes.ok ? ((await specRes.json()) as { items: Array<SpecialtyRef & { doctorCount: number; parentSlug?: string | null }> }).items : [])
    .filter((s) => s.doctorCount > 0);

  const locParams = new URLSearchParams();
  appendList(locParams, "specialty", specialty);
  appendList(locParams, "clinic", clinic);
  if (treatsChildren) locParams.set("treatsChildren", "true");
  if (treatsAdults) locParams.set("treatsAdults", "true");
  const locRes = await fetch(`${API_BASE}/api/v1/locations${locParams.toString() ? `?${locParams}` : ""}`);
  const regions = locRes.ok ? ((await locRes.json()) as { items: LocationRegion[] }).items : [];

  const clinicParams = new URLSearchParams({ located: "true" }); // the map only filters by clinics it can place
  if (region) clinicParams.set("region", region);
  if (city) clinicParams.set("city", city);
  appendList(clinicParams, "specialty", specialty);
  if (treatsChildren) clinicParams.set("treatsChildren", "true");
  if (treatsAdults) clinicParams.set("treatsAdults", "true");
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
    selectedTreatsChildren: treatsChildren,
    selectedTreatsAdults: treatsAdults,
  };
};
