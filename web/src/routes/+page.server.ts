import type { PageServerLoad } from "./$types";

const API_BASE = process.env.API_URL ?? "http://localhost:8080";

interface DoctorDto {
  slug: string;
  fullName: string;
}

export const load: PageServerLoad = async ({ fetch }) => {
  try {
    const res = await fetch(`${API_BASE}/api/v1/doctors/test-doctor`);
    if (!res.ok) {
      return { doctor: null, apiBase: API_BASE };
    }
    const doctor = (await res.json()) as DoctorDto;
    return { doctor, apiBase: API_BASE };
  } catch {
    return { doctor: null, apiBase: API_BASE };
  }
};
