import { error, redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

import { API_BASE } from "$lib/server/api";

interface SpecialtyRef {
  slug: string;
  nameKa: string;
  nameEn: string;
  isPrimary: boolean;
}

interface DoctorProfile {
  slug: string;
  fullNameKa: string;
  fullNameEn: string;
  gender: string | null;
  photoUrl: string | null;
  isAcceptingNewPatients: boolean;
  treatsChildren: boolean;
  treatsAdults: boolean;
  bioKa: string | null;
  bioEn: string | null;
  specialtyKa: string | null;
  specialtyEn: string | null;
  specialties: SpecialtyRef[];
  clinics: Array<{ slug: string; nameKa: string; nameEn: string; address: string | null; addressEn: string | null; phone: string | null }>;
  lastSourceUrl: string | null;
  lastUpdatedAt: string | null;
}

export const load: PageServerLoad = async ({ params, fetch }) => {
  const slug = encodeURIComponent(params.slug);
  const [res, similarRes] = await Promise.all([
    fetch(`${API_BASE}/api/v1/doctors/${slug}`, { redirect: "manual" }),
    fetch(`${API_BASE}/api/v1/doctors/${slug}/similar?limit=12`),
  ]);
  if (res.status === 301) {
    const loc = res.headers.get("location") ?? "";
    const canonical = loc.split("/").pop();
    if (canonical && canonical !== params.slug) throw redirect(301, `/doctors/${canonical}`);
  }
  if (res.status === 404) {
    error(404, "Doctor not found");
  }
  if (!res.ok) {
    error(res.status, "Could not load doctor");
  }
  const doctor = (await res.json()) as DoctorProfile;
  const similar = similarRes.ok ? await similarRes.json() : [];

  return { doctor, similar };
};
