import { json } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";
import { appendList } from "$lib/listParams";

import { API_BASE } from "$lib/server/api";

export const GET: RequestHandler = async ({ url, fetch }) => {
  const params = new URLSearchParams();
  appendList(params, "specialty", url.searchParams.get("specialty"));
  appendList(params, "clinic", url.searchParams.get("clinic"));
  if (url.searchParams.get("treatsChildren") === "true") params.set("treatsChildren", "true");
  if (url.searchParams.get("treatsAdults") === "true") params.set("treatsAdults", "true");
  const query = params.toString();
  try {
    const res = await fetch(`${API_BASE}/api/v1/locations${query ? `?${query}` : ""}`);
    if (!res.ok) return json({ items: [] });
    return json(await res.json());
  } catch {
    return json({ items: [] });
  }
};
