import type { PageServerLoad } from "./$types";
import { error } from "@sveltejs/kit";
import { appendList } from "$lib/listParams";

import { API_BASE } from "$lib/server/api";

export const load: PageServerLoad = async ({ params, url, fetch }) => {
  const slug = params.slug;
  const rawPage = Number(url.searchParams.get("page") ?? "1");
  const page = Number.isFinite(rawPage) && rawPage >= 1 ? rawPage : 1;

  const params2 = new URLSearchParams({ page: String(page), pageSize: "6", clinic: slug });
  appendList(params2, "specialty", url.searchParams.get("specialty"));
  const [detailRes, listRes] = await Promise.all([
    fetch(`${API_BASE}/api/v1/clinics/${slug}`),
    fetch(`${API_BASE}/api/v1/doctors?${params2.toString()}`),
  ]);
  if (detailRes.status === 404) throw error(404, "Clinic not found");
  const detail = await detailRes.json();
  const list = listRes.ok ? await listRes.json() : { items: [], page, pageSize: 6, total: 0 };

  return { detail, list };
};
