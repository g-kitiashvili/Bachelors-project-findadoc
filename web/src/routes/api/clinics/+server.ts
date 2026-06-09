import { json } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";
import { appendList } from "$lib/listParams";

const API_BASE = process.env.API_URL ?? "http://localhost:8080";

export const GET: RequestHandler = async ({ url, fetch }) => {
  const p = new URLSearchParams();
  for (const k of ["q", "region", "city", "treatsChildren", "treatsAdults"]) {
    const v = (url.searchParams.get(k) ?? "").trim();
    if (v) p.set(k, v);
  }
  appendList(p, "specialty", url.searchParams.get("specialty"));
  const qs = p.toString();
  try {
    const res = await fetch(`${API_BASE}/api/v1/clinics${qs ? `?${qs}` : ""}`);
    if (!res.ok) return json({ items: [] });
    return json(await res.json());
  } catch {
    return json({ items: [] });
  }
};
