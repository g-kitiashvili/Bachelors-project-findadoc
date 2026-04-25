import { json } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";

const API_BASE = process.env.API_URL ?? "http://localhost:8080";

export const GET: RequestHandler = async ({ url, fetch }) => {
  const params = new URLSearchParams();
  const region = (url.searchParams.get("region") ?? "").trim();
  const city = (url.searchParams.get("city") ?? "").trim();
  if (region) params.set("region", region);
  if (city) params.set("city", city);
  const query = params.toString();
  try {
    const res = await fetch(`${API_BASE}/api/v1/specialties${query ? `?${query}` : ""}`);
    if (!res.ok) return json({ items: [] });
    return json(await res.json());
  } catch {
    return json({ items: [] });
  }
};
