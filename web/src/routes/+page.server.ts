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
  specialtyKa: string | null;
  specialtyEn: string | null;
}

interface DoctorPage {
  items: DoctorListItem[];
  page: number;
  pageSize: number;
  total: number;
}

export const load: PageServerLoad = async ({ fetch }) => {
  // Pull a small batch of doctors for the hero collage initials + the total count.
  const res = await fetch(`${API_BASE}/api/v1/doctors?page=1&pageSize=3`);
  if (!res.ok) {
    return { total: 0, sample: [] as DoctorListItem[] };
  }
  const page = (await res.json()) as DoctorPage;
  return { total: page.total, sample: page.items };
};
