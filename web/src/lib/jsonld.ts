/**
 * Serialize a Schema.org object into a `<script type="application/ld+json">` string for
 * `{@html ...}` in <svelte:head>. `<` is escaped so data can never break out of the script tag.
 */
export function jsonLdScript(data: Record<string, unknown>): string {
  const json = JSON.stringify({ "@context": "https://schema.org", ...data }).replace(/</g, "\\u003c");
  return `<script type="application/ld+json">${json}<\/script>`;
}
