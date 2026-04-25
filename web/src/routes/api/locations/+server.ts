import { json } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";

const API_BASE = process.env.API_URL ?? "http://localhost:8080";

export const GET: RequestHandler = async ({ url, fetch }) => {
  const specialty = (url.searchParams.get("specialty") ?? "").trim();
  const query = specialty ? `?specialty=${encodeURIComponent(specialty)}` : "";
  try {
    const res = await fetch(`${API_BASE}/api/v1/locations${query}`);
    if (!res.ok) return json({ items: [] });
    return json(await res.json());
  } catch {
    return json({ items: [] });
  }
};
