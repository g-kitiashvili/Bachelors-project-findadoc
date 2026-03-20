import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

const API_BASE = process.env.API_URL ?? "http://localhost:8080";

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
}

export const load: PageServerLoad = async ({ params, fetch }) => {
  const res = await fetch(
    `${API_BASE}/api/v1/doctors/${encodeURIComponent(params.slug)}`,
  );
  if (res.status === 404) {
    error(404, "Doctor not found");
  }
  if (!res.ok) {
    error(res.status, "Could not load doctor");
  }
  return { doctor: (await res.json()) as DoctorProfile };
};
