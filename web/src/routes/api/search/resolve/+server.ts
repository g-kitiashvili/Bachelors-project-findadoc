import { json } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";

import { API_BASE } from "$lib/server/api";

export const GET: RequestHandler = async ({ url, fetch }) => {
  const q = (url.searchParams.get("q") ?? "").trim().slice(0, 100);
  if (q.length < 2) return json({ type: "query", slug: null, label: q });
  try {
    const res = await fetch(`${API_BASE}/api/v1/search/resolve?q=${encodeURIComponent(q)}`);
    if (!res.ok) return json({ type: "query", slug: null, label: q });
    return json(await res.json());
  } catch {
    return json({ type: "query", slug: null, label: q });
  }
};
