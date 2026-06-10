import type { PageServerLoad } from "./$types";

import { API_BASE } from "$lib/server/api";

export const load: PageServerLoad = async ({ fetch }) => {
  const res = await fetch(`${API_BASE}/api/v1/conditions`);
  if (!res.ok) return { conditions: [] };
  const body = (await res.json()) as { items: Array<{ slug: string; nameKa: string; nameEn: string; doctorCount: number }> };
  return { conditions: body.items };
};
