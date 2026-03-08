import type { PageServerLoad } from "./$types";

const API_BASE = process.env.API_URL ?? "http://localhost:8080";

interface DoctorListItem {
  slug: string;
  fullNameKa: string;
  fullNameEn: string;
  photoUrl: string | null;
  isAcceptingNewPatients: boolean;
  treatsChildren: boolean;
  treatsAdults: boolean;
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
  const res = await fetch(`${API_BASE}/api/v1/doctors?page=${page}&pageSize=5`);
  if (!res.ok) {
    return { items: [], page, pageSize: 5, total: 0 } as DoctorPage;
  }
  return (await res.json()) as DoctorPage;
};
