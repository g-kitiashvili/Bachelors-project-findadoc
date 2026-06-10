import type { RequestHandler } from "./$types";
import { API_BASE } from "$lib/server/api";

const STATIC_PATHS = [
  "",
  "doctors",
  "doctors/map",
  "specialties",
  "conditions",
  "clinics",
  "symptoms",
  "privacy",
  "terms",
  "takedown",
];
const LOCALES = ["ka", "en"];

// The brand-collapsed taxonomy is small and bounded; individual doctor profiles (3k+) are
// omitted to keep generation cheap - add them via a bulk-slug endpoint if crawl coverage needs it.
export const GET: RequestHandler = async ({ url, fetch }) => {
  const slugs = async (path: string): Promise<string[]> => {
    const r = await fetch(`${API_BASE}${path}`);
    if (!r.ok) return [];
    const items = ((await r.json()) as { items?: Array<{ slug: string }> }).items ?? [];
    return items.map((i) => i.slug);
  };

  const [specialties, conditions, clinics] = await Promise.all([
    slugs("/api/v1/specialties"),
    slugs("/api/v1/conditions"),
    slugs("/api/v1/clinics?collapse=true&pageSize=500"),
  ]);

  const paths = [
    ...STATIC_PATHS,
    ...specialties.map((s) => `specialties/${s}`),
    ...conditions.map((s) => `conditions/${s}`),
    ...clinics.map((s) => `clinics/${s}`),
  ];

  const entries = paths.flatMap((p) => {
    const suffix = p ? `/${p}` : "";
    return LOCALES.map((loc) => `  <url><loc>${url.origin}/${loc}${suffix}</loc></url>`);
  });

  const body =
    '<?xml version="1.0" encoding="UTF-8"?>\n' +
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    entries.join("\n") +
    "\n</urlset>\n";

  return new Response(body, {
    headers: { "Content-Type": "application/xml", "Cache-Control": "max-age=3600" },
  });
};
