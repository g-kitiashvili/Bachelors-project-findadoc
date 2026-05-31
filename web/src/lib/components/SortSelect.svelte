<script lang="ts">
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  import * as m from "$lib/paraglide/messages";
  import MultiSelect from "./MultiSelect.svelte";

  let { value, hasQuery }: { value: string; hasQuery: boolean } = $props();

  const options = $derived([
    ...(hasQuery ? [{ value: "relevancy", label: m.sort_relevancy() }] : []),
    { value: "atoz", label: m.sort_atoz() },
    { value: "ztoa", label: m.sort_ztoa() },
  ]);

  function onChange(next: string[]) {
    const sort = next[0] ?? "";
    const url = new URL($page.url);
    if (sort) url.searchParams.set("sort", sort);
    else url.searchParams.delete("sort");
    url.searchParams.delete("page");
    goto(url.pathname + url.search);
  }
</script>

<div class="sort">
  <span>{m.sort_label()}</span>
  <div class="sort-ctl">
    <MultiSelect
      placeholder={m.sort_atoz()}
      multiple={false}
      searchable={false}
      compact
      {options}
      selected={value ? [value] : []}
      {onChange}
    />
  </div>
</div>

<style>
  .sort { display: inline-flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; color: var(--ink-muted); }
  .sort-ctl { width: 150px; }
</style>
