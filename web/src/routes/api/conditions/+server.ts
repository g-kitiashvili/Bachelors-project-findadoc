import { json, type RequestHandler } from "@sveltejs/kit";

const API_BASE = process.env.API_URL ?? "http://localhost:8080";

export const GET: RequestHandler = async ({ fetch }) => {
  try {
    const res = await fetch(`${API_BASE}/api/v1/conditions`);
    return json(await res.json());
  } catch {
    return json({ items: [] });
  }
};
