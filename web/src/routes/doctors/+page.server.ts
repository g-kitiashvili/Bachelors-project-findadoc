import type { PageServerLoad } from "./$types";

const API_BASE = process.env.API_URL ?? "http://localhost:8080";

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

  const params = new URLSearchParams({ page: String(page), pageSize: "12" });
  if (q) params.set("q", q);
  if (specialty) params.set("specialty", specialty);
  if (region) params.set("region", region);
  if (city) params.set("city", city);
  if (sort) params.set("sort", sort);
  if (clinic) params.set("clinic", clinic);

  const res = await fetch(`${API_BASE}/api/v1/doctors?${params.toString()}`);
  const data = res.ok
    ? ((await res.json()) as DoctorPage)
    : { items: [], page, pageSize: 12, total: 0 };

  const selectedSlugs = specialty ? specialty.split(",").filter(Boolean) : [];
  const selectedSort = q ? sort || "relevancy" : sort === "ztoa" ? "ztoa" : "atoz";

  const specParams = new URLSearchParams();
  if (region) specParams.set("region", region);
  if (city) specParams.set("city", city);
  if (clinic) specParams.set("clinic", clinic);
  const specQuery = specParams.toString();
  const specRes = await fetch(
    `${API_BASE}/api/v1/specialties${specQuery ? `?${specQuery}` : ""}`,
  );
  const specialties = (
    specRes.ok
      ? ((await specRes.json()) as { items: Array<SpecialtyRef & { doctorCount: number }> }).items
      : []
  ).filter((s) => s.doctorCount > 0);

  const locParams = new URLSearchParams();
  if (specialty) locParams.set("specialty", specialty);
  if (clinic) locParams.set("clinic", clinic);
  const locRes = await fetch(`${API_BASE}/api/v1/locations${locParams.toString() ? `?${locParams}` : ""}`);
  const regions = locRes.ok
    ? ((await locRes.json()) as { items: LocationRegion[] }).items
    : [];

  const clinicParams = new URLSearchParams();
  if (region) clinicParams.set("region", region);
  if (city) clinicParams.set("city", city);
  if (specialty) clinicParams.set("specialty", specialty);
  const clinicsRes = await fetch(`${API_BASE}/api/v1/clinics${clinicParams.toString() ? `?${clinicParams}` : ""}`);
  const clinics = clinicsRes.ok
    ? ((await clinicsRes.json()) as { items: ClinicRef[] }).items
    : [];

  return { ...data, q, selectedSlugs, specialties, regions, selectedRegion: region, selectedCity: city, sort, selectedSort, clinics, selectedClinics: clinic ? clinic.split(",").filter(Boolean) : [] };
};
