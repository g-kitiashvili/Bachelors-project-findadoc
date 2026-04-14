<script lang="ts">
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";

  let { value, hasQuery }: { value: string; hasQuery: boolean } = $props();

  function onChange(next: string) {
    const url = new URL($page.url);
    if (next) url.searchParams.set("sort", next);
    else url.searchParams.delete("sort");
    url.searchParams.delete("page");
    goto(url.pathname + url.search);
  }
</script>

<label class="sort">
  <span>Sort</span>
  <select value={value} onchange={(e) => onChange(e.currentTarget.value)}>
    {#if hasQuery}
      <option value="relevancy">Relevancy</option>
    {/if}
    <option value="atoz">A→Z</option>
    <option value="ztoa">Z→A</option>
  </select>
</label>

<style>
  .sort { display: inline-flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; color: var(--ink-muted); }
  .sort select { font: inherit; padding: 0.35rem 0.5rem; border: 1px solid var(--line); border-radius: 6px; background: var(--surface); color: var(--ink); }
</style>
