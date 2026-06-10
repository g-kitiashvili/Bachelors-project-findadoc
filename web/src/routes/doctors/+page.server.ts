import type { PageServerLoad } from "./$types";
import { appendList } from "$lib/listParams";

import { API_BASE } from "$lib/server/api";

export interface SpecialtyRef {
  slug: string;
  nameKa: string;
  nameEn: string;
}

export interface ClinicRef {
  slug: string;
  nameKa: string;
  nameEn: string;
  doctorCount: number;
}

export interface LocationCity { slug: string; nameKa: string; nameEn: string; doctorCount: number }
export interface LocationRegion extends LocationCity { cities: LocationCity[] }

interface DoctorListItem {
  slug: string;
  fullNameKa: string;
  fullNameEn: string;
  photoUrl: string | null;
  isAcceptingNewPatients: boolean;
  treatsChildren: boolean;
  treatsAdults: boolean;
  specialtyKa: string | null;
  specialtyEn: string | null;
  primarySpecialty: SpecialtyRef | null;
  primaryClinic: { slug: string; nameKa: string; nameEn: string; address: string | null } | null;
}

interface DoctorPage {
  items: DoctorListItem[];
  page: number;
  pageSize: number;
  total: number;
}

export const load: PageServerLoad = async ({ url, fetch }) => {
  const rawPage = Number(url.searchParams.get("page") ?? "1");
  const page = Number.isFinite(rawPage) && rawPage >= 1 ? rawPage : 1;
  const q = (url.searchParams.get("q") ?? "").trim();
  const specialty = (url.searchParams.get("specialty") ?? "").trim();
  const region = (url.searchParams.get("region") ?? "").trim();
  const city = (url.searchParams.get("city") ?? "").trim();
  const sort = (url.searchParams.get("sort") ?? "").trim();
  const clinic = (url.searchParams.get("clinic") ?? "").trim();
  const treatsChildren = url.searchParams.get("treatsChildren") === "true";
  const treatsAdults = url.searchParams.get("treatsAdults") === "true";

  const params = new URLSearchParams({ page: String(page), pageSize: "12" });
  if (q) params.set("q", q);
  appendList(params, "specialty", specialty);
  if (region) params.set("region", region);
  if (city) params.set("city", city);
  if (sort) params.set("sort", sort);
  appendList(params, "clinic", clinic);
  if (treatsChildren) params.set("treatsChildren", "true");
  if (treatsAdults) params.set("treatsAdults", "true");

  const specParams = new URLSearchParams();
  if (region) specParams.set("region", region);
  if (city) specParams.set("city", city);
  appendList(specParams, "clinic", clinic);
  if (treatsChildren) specParams.set("treatsChildren", "true");
  if (treatsAdults) specParams.set("treatsAdults", "true");

  const locParams = new URLSearchParams();
  appendList(locParams, "specialty", specialty);
  appendList(locParams, "clinic", clinic);
  if (treatsChildren) locParams.set("treatsChildren", "true");
  if (treatsAdults) locParams.set("treatsAdults", "true");

  const clinicParams = new URLSearchParams();
  if (region) clinicParams.set("region", region);
  if (city) clinicParams.set("city", city);
  appendList(clinicParams, "specialty", specialty);
  if (treatsChildren) clinicParams.set("treatsChildren", "true");
  if (treatsAdults) clinicParams.set("treatsAdults", "true");

  const qs = (p: URLSearchParams) => (p.toString() ? `?${p}` : "");
  const json = async <T>(path: string, fallback: T): Promise<T> => {
    const r = await fetch(`${API_BASE}${path}`);
    return r.ok ? ((await r.json()) as T) : fallback;
  };

  // Independent lookups - fetch in parallel rather than waterfalling.
  const [data, specialtiesData, regionsData, clinicsData] = await Promise.all([
    json<DoctorPage>(`/api/v1/doctors?${params}`, { items: [], page, pageSize: 12, total: 0 }),
    json<{ items: Array<SpecialtyRef & { doctorCount: number }> }>(`/api/v1/specialties${qs(specParams)}`, { items: [] }),
    json<{ items: LocationRegion[] }>(`/api/v1/locations${qs(locParams)}`, { items: [] }),
    json<{ items: ClinicRef[] }>(`/api/v1/clinics${qs(clinicParams)}`, { items: [] }),
  ]);

  const specialties = specialtiesData.items.filter((s) => s.doctorCount > 0);
  const selectedSlugs = specialty ? specialty.split(",").filter(Boolean) : [];
  const selectedSort = sort || (q ? "relevancy" : "top");

  return { ...data, q, selectedSlugs, specialties, regions: regionsData.items, selectedRegion: region, selectedCity: city, sort, selectedSort, clinics: clinicsData.items, selectedClinics: clinic ? clinic.split(",").filter(Boolean) : [], selectedTreatsChildren: treatsChildren, selectedTreatsAdults: treatsAdults };
};
