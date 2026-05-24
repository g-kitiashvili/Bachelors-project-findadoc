import type { PageServerLoad } from "./$types";

const API_BASE = process.env.API_URL ?? "http://localhost:8080";

export const load: PageServerLoad = async ({ url, fetch }) => {
  const rawPage = Number(url.searchParams.get("page") ?? "1");
  const page = Number.isFinite(rawPage) && rawPage >= 1 ? rawPage : 1;
  const q = (url.searchParams.get("q") ?? "").trim();
  const pageSize = 24;
  const params = new URLSearchParams({ page: String(page), pageSize: String(pageSize) });
  if (q) params.set("q", q);
  const res = await fetch(`${API_BASE}/api/v1/clinics?${params}`);
  const data = res.ok
    ? ((await res.json()) as { items: Array<{ slug: string; nameKa: string; nameEn: string; doctorCount: number }>; page: number; pageSize: number; total: number })
    : { items: [], page, pageSize, total: 0 };
  return { ...data, q };
};
