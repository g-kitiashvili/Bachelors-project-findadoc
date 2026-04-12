import type { PageServerLoad } from "./$types";

const API_BASE = process.env.API_URL ?? "http://localhost:8080";

export interface SpecialtyRef {
  slug: string;
  nameKa: string;
  nameEn: string;
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

  const params = new URLSearchParams({ page: String(page), pageSize: "5" });
  if (q) params.set("q", q);
  if (specialty) params.set("specialty", specialty);
  if (region) params.set("region", region);
  if (city) params.set("city", city);

  const res = await fetch(`${API_BASE}/api/v1/doctors?${params.toString()}`);
  const data = res.ok
    ? ((await res.json()) as DoctorPage)
    : { items: [], page, pageSize: 5, total: 0 };

  const selectedSlugs = specialty ? specialty.split(",").filter(Boolean) : [];

  const specRes = await fetch(`${API_BASE}/api/v1/specialties`);
  const specialties = (
    specRes.ok
      ? ((await specRes.json()) as { items: Array<SpecialtyRef & { doctorCount: number }> }).items
      : []
  ).filter((s) => s.doctorCount > 0);

  const locRes = await fetch(`${API_BASE}/api/v1/locations`);
  const regions = locRes.ok
    ? ((await locRes.json()) as { items: LocationRegion[] }).items
    : [];

  return { ...data, q, selectedSlugs, specialties, regions, selectedRegion: region, selectedCity: city };
};
