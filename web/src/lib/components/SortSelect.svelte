<script lang="ts">
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  import * as m from "$lib/paraglide/messages";
  import MultiSelect from "./MultiSelect.svelte";

  let { value, hasQuery }: { value: string; hasQuery: boolean } = $props();

  // Default order is relevance while searching, otherwise the prominence rank
  // ("Recommended"). Both are the no-sort-param state; an empty `value` means default.
  const defaultValue = $derived(hasQuery ? "relevancy" : "top");
  const defaultLabel = $derived(hasQuery ? m.sort_relevancy() : m.sort_top());
  const options = $derived([
    { value: defaultValue, label: defaultLabel },
    { value: "atoz", label: m.sort_atoz() },
    { value: "ztoa", label: m.sort_ztoa() },
  ]);

  function onChange(next: string[]) {
    const sort = next[0] ?? "";
    const url = new URL($page.url);
    if (!sort || sort === defaultValue) url.searchParams.delete("sort");
    else url.searchParams.set("sort", sort);
    url.searchParams.delete("page");
    goto(url.pathname + url.search);
  }
</script>

<div class="sort">
  <span>{m.sort_label()}</span>
  <div class="sort-ctl">
    <MultiSelect
      placeholder={defaultLabel}
      multiple={false}
      searchable={false}
      compact
      {options}
      selected={[value || defaultValue]}
      {onChange}
    />
  </div>
</div>

<style>
  .sort { display: inline-flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; color: var(--ink-muted); }
  .sort-ctl { width: 150px; }
</style>
