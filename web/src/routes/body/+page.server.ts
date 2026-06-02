import type { PageServerLoad } from './$types';
import type { TriageGraph } from '$lib/triage';

const API_BASE = process.env.API_URL ?? 'http://localhost:8080';
type NameItem = { slug: string; nameKa: string; nameEn: string };

async function nameMap(fetch: typeof globalThis.fetch, path: string, type: string): Promise<Record<string, { ka: string; en: string }>> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) return {};
  const body = (await res.json()) as { items: NameItem[] };
  const out: Record<string, { ka: string; en: string }> = {};
  for (const it of body.items) out[`${type}:${it.slug}`] = { ka: it.nameKa, en: it.nameEn };
  return out;
}

export const load: PageServerLoad = async ({ fetch }) => {
  const [graphRes, specialties, conditions] = await Promise.all([
    fetch(`${API_BASE}/api/v1/triage`),
    nameMap(fetch, '/api/v1/specialties', 'specialty'),
    nameMap(fetch, '/api/v1/conditions', 'condition'),
  ]);
  const graph = (graphRes.ok ? await graphRes.json() : { start: '', nodes: {} }) as TriageGraph;
  return { graph, names: { ...specialties, ...conditions } };
};
