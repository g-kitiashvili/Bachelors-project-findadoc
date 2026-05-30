import { json } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";

const API_BASE = process.env.API_URL ?? "http://localhost:8080";

export const GET: RequestHandler = async ({ url, fetch }) => {
  const params = new URLSearchParams();
  const region = (url.searchParams.get("region") ?? "").trim();
  const city = (url.searchParams.get("city") ?? "").trim();
  const clinic = (url.searchParams.get("clinic") ?? "").trim();
  if (region) params.set("region", region);
  if (city) params.set("city", city);
  if (clinic) params.set("clinic", clinic);
  if (url.searchParams.get("treats_children") === "true") params.set("treats_children", "true");
  if (url.searchParams.get("treats_adults") === "true") params.set("treats_adults", "true");
  const query = params.toString();
  try {
    const res = await fetch(`${API_BASE}/api/v1/specialties${query ? `?${query}` : ""}`);
    if (!res.ok) return json({ items: [] });
    return json(await res.json());
  } catch {
    return json({ items: [] });
  }
};
