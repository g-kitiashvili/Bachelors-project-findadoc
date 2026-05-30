import { json } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";

const API_BASE = process.env.API_URL ?? "http://localhost:8080";

export const GET: RequestHandler = async ({ url, fetch }) => {
  const params = new URLSearchParams();
  const specialty = (url.searchParams.get("specialty") ?? "").trim();
  const clinic = (url.searchParams.get("clinic") ?? "").trim();
  if (specialty) params.set("specialty", specialty);
  if (clinic) params.set("clinic", clinic);
  if (url.searchParams.get("treats_children") === "true") params.set("treats_children", "true");
  if (url.searchParams.get("treats_adults") === "true") params.set("treats_adults", "true");
  const query = params.toString();
  try {
    const res = await fetch(`${API_BASE}/api/v1/locations${query ? `?${query}` : ""}`);
    if (!res.ok) return json({ items: [] });
    return json(await res.json());
  } catch {
    return json({ items: [] });
  }
};
