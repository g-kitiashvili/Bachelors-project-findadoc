import type { PageServerLoad } from "./$types";

import { API_BASE } from "$lib/server/api";

export const load: PageServerLoad = async ({ fetch }) => {
  const res = await fetch(`${API_BASE}/api/v1/specialties`);
  if (!res.ok) return { specialties: [] };
  const body = (await res.json()) as { items: Array<{ slug: string; nameKa: string; nameEn: string; doctorCount: number }> };
  return { specialties: body.items };
};
