<script lang="ts">
  let {
    page,
    pageSize,
    total,
    q = "",
    specialty = "",
    region = "",
    city = "",
    sort = "",
  }: { page: number; pageSize: number; total: number; q?: string; specialty?: string; region?: string; city?: string; sort?: string } = $props();

  const totalPages = $derived(Math.max(1, Math.ceil(total / pageSize)));
  const prevDisabled = $derived(page <= 1);
  const nextDisabled = $derived(page >= totalPages);

  function linkFor(p: number): string {
    const params = new URLSearchParams();
    params.set("page", String(p));
    if (q) params.set("q", q);
    if (specialty) params.set("specialty", specialty);
    if (region) params.set("region", region);
    if (city) params.set("city", city);
    if (sort) params.set("sort", sort);
    return `?${params.toString()}`;
  }

  function pageWindow(current: number, last: number): (number | "ellipsis")[] {
    const wanted = new Set<number>([1, last]);
    for (let p = current - 2; p <= current + 2; p++) {
      if (p >= 1 && p <= last) wanted.add(p);
    }
    const sorted = [...wanted].sort((a, b) => a - b);
    const out: (number | "ellipsis")[] = [];
    let prev = 0;
    for (const p of sorted) {
      if (p - prev === 2) out.push(prev + 1);
      else if (p - prev > 2) out.push("ellipsis");
      out.push(p);
      prev = p;
    }
    return out;
  }

  const pageItems = $derived(pageWindow(page, totalPages));
</script>

{#if total > 0 && totalPages > 1}
  <nav class="pagination" aria-label="Pagination">
    <a
      href={prevDisabled ? null : linkFor(page - 1)}
      class:disabled={prevDisabled}
      aria-disabled={prevDisabled}>
      ← Prev
    </a>

    <ul class="pages">
      {#each pageItems as item, i (item === "ellipsis" ? `e${i}` : item)}
        {#if item === "ellipsis"}
          <li class="ellipsis" aria-hidden="true">…</li>
        {:else if item === page}
          <li><span class="current" aria-current="page">{item}</span></li>
        {:else}
          <li><a href={linkFor(item)}>{item}</a></li>
        {/if}
      {/each}
    </ul>

    <a
      href={nextDisabled ? null : linkFor(page + 1)}
      class:disabled={nextDisabled}
      aria-disabled={nextDisabled}>
      Next →
    </a>
  </nav>
{/if}

<style>
  .pagination {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    margin: 2.5rem 0 1rem;
  }
  .pagination > a {
    padding: 0.55rem 1rem;
    border: 1px solid var(--line);
    border-radius: 8px;
    color: var(--ink);
    font-size: 0.92rem;
    font-weight: 500;
    transition: all 0.15s;
    background: var(--surface);
  }
  .pagination > a:not(.disabled):hover {
    border-color: var(--accent);
    color: var(--accent);
    background: var(--accent-soft);
  }
  .pagination > a.disabled {
    color: var(--ink-faint);
    pointer-events: none;
    background: var(--bg-soft);
  }
  .pages {
    display: flex;
    gap: 0.25rem;
    align-items: center;
    list-style: none;
    margin: 0;
    padding: 0;
  }
  .pages a, .pages .current {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 2.25rem;
    height: 2.25rem;
    padding: 0 0.5rem;
    border: 1px solid var(--line);
    border-radius: 8px;
    font-size: 0.9rem;
    background: var(--surface);
    color: var(--ink);
  }
  .pages a:hover {
    border-color: var(--accent);
    color: var(--accent);
    background: var(--accent-soft);
  }
  .pages .current {
    background: var(--accent);
    border-color: var(--accent);
    color: white;
    font-weight: 600;
  }
  .pages .ellipsis {
    min-width: 1.5rem;
    text-align: center;
    color: var(--ink-faint);
  }
</style>
