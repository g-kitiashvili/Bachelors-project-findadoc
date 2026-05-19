import type { PageServerLoad } from "./$types";

const API_BASE = process.env.API_URL ?? "http://localhost:8080";

export const load: PageServerLoad = async ({ fetch }) => {
  const res = await fetch(`${API_BASE}/api/v1/conditions`);
  if (!res.ok) return { conditions: [] };
  const body = (await res.json()) as { items: Array<{ slug: string; nameKa: string; nameEn: string; doctorCount: number }> };
  return { conditions: body.items };
};
