import { json, type RequestHandler } from "@sveltejs/kit";

import { API_BASE } from "$lib/server/api";

export const GET: RequestHandler = async ({ fetch }) => {
  try {
    const res = await fetch(`${API_BASE}/api/v1/conditions`);
    return json(await res.json());
  } catch {
    return json({ items: [] });
  }
};
