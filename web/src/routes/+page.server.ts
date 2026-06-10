import type { PageServerLoad } from "./$types";

import { API_BASE } from "$lib/server/api";

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
  // Doctors (count + hero collage initials) + live specialty/clinic counts for the stats strip.
  const [docRes, specRes, condRes] = await Promise.all([
    fetch(`${API_BASE}/api/v1/doctors?page=1&pageSize=3`),
    fetch(`${API_BASE}/api/v1/specialties`),
    fetch(`${API_BASE}/api/v1/conditions`),
  ]);
  const page = docRes.ok
    ? ((await docRes.json()) as DoctorPage)
    : { items: [] as DoctorListItem[], page: 1, pageSize: 3, total: 0 };
  const specialties = specRes.ok
    ? ((await specRes.json()) as { items: Array<{ doctorCount: number }> }).items
    : [];
  const conditions = condRes.ok ? ((await condRes.json()) as { items: unknown[] }).items : [];
  return {
    total: page.total,
    sample: page.items,
    specialtyCount: specialties.filter((s) => s.doctorCount > 0).length,
    conditionCount: conditions.length,
  };
};
