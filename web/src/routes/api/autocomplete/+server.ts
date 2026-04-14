import { json } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";

const API_BASE = process.env.API_URL ?? "http://localhost:8080";

export const GET: RequestHandler = async ({ url, fetch }) => {
  const q = (url.searchParams.get("q") ?? "").trim().slice(0, 100);
  if (q.length < 2) return json({ doctors: [], specialties: [] });
  try {
    const res = await fetch(`${API_BASE}/api/v1/autocomplete?q=${encodeURIComponent(q)}`);
    if (!res.ok) return json({ doctors: [], specialties: [] });
    return json(await res.json());
  } catch {
    return json({ doctors: [], specialties: [] });
  }
};
