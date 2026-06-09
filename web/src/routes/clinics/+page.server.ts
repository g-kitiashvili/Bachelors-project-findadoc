import type { PageServerLoad } from "./$types";

const API_BASE = process.env.API_URL ?? "http://localhost:8080";

type Branch = { slug: string; nameKa: string; nameEn: string; address: string | null };
type Clinic = { slug: string; nameKa: string; nameEn: string; doctorCount: number; branches?: Branch[] };
type ClinicsPage = { items: Clinic[]; page: number; pageSize: number; total: number };

export const load: PageServerLoad = async ({ fetch }) => {
  const params = new URLSearchParams({ page: "1", pageSize: "500", collapse: "true" });
  const res = await fetch(`${API_BASE}/api/v1/clinics?${params}`);
  const data = res.ok
    ? ((await res.json()) as ClinicsPage)
    : ({ items: [], page: 1, pageSize: 500, total: 0 } as ClinicsPage);
  return { items: data.items, total: data.total };
};
