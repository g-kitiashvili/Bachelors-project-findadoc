import type { PageServerLoad } from "./$types";
import { error } from "@sveltejs/kit";

const API_BASE = process.env.API_URL ?? "http://localhost:8080";

export const load: PageServerLoad = async ({ params, url, fetch }) => {
  const slug = params.slug;
  const rawPage = Number(url.searchParams.get("page") ?? "1");
  const page = Number.isFinite(rawPage) && rawPage >= 1 ? rawPage : 1;

  const detailRes = await fetch(`${API_BASE}/api/v1/clinics/${slug}`);
  if (detailRes.status === 404) throw error(404, "Clinic not found");
  const detail = await detailRes.json();

  const params2 = new URLSearchParams({ page: String(page), pageSize: "5", clinic: slug });
  const specialty = (url.searchParams.get("specialty") ?? "").trim();
  if (specialty) params2.set("specialty", specialty);
  const listRes = await fetch(`${API_BASE}/api/v1/doctors?${params2.toString()}`);
  const list = listRes.ok ? await listRes.json() : { items: [], page, pageSize: 5, total: 0 };

  return { detail, list };
};
