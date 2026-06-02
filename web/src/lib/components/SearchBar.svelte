<script lang="ts">
  import { goto } from "$app/navigation";
  import * as m from "$lib/paraglide/messages";
  import { href, localizedField } from "$lib/i18n";
  import { getLocale } from "$lib/paraglide/runtime";

  let {
    initialValue = "",
    placeholder = m.search_placeholder(),
    autofocus = false,
    mapMode = false,
  }: { initialValue?: string; placeholder?: string; autofocus?: boolean; mapMode?: boolean } = $props();

  interface DoctorSuggestion { slug: string; fullNameEn: string; fullNameKa: string; primarySpecialtyEn: string | null; primarySpecialtyKa: string | null }
  interface EntitySuggestion { slug: string; nameEn: string; nameKa: string; doctorCount: number }

  // On the map page, a pick filters the map (stays on /doctors/map) instead of navigating away.
  const specialtyHref = (slug: string) =>
    mapMode ? href("/doctors/map") + `?specialty=${slug}` : href("/doctors") + `?specialty=${slug}`;
  const conditionHref = (slug: string) =>
    mapMode ? href("/doctors/map") + `?condition=${slug}` : href(`/conditions/${slug}`);

  let value = $state(initialValue);
  let results = $state<{ doctors: DoctorSuggestion[]; specialties: EntitySuggestion[]; conditions: EntitySuggestion[] }>(
    { doctors: [], specialties: [], conditions: [] },
  );
  let open = $state(false);
  let highlighted = $state(-1);
  let wrapper: HTMLElement;

  let debounceTimer: ReturnType<typeof setTimeout> | undefined;
  let controller: AbortController | undefined;

  const flat = $derived([
    ...results.doctors.map((d) => href(`/doctors/${d.slug}`)),
    ...results.specialties.map((s) => specialtyHref(s.slug)),
    ...results.conditions.map((c) => conditionHref(c.slug)),
  ]);

  const hasResults = $derived(
    results.doctors.length > 0 || results.specialties.length > 0 ||
    results.conditions.length > 0,
  );

  function countLabel(n: number) {
    return `${n} ${n === 1 ? m.noun_doctor() : m.noun_doctors()}`;
  }

  function onInput() {
    if (debounceTimer) clearTimeout(debounceTimer);
    const term = value.trim();
    if (term.length < 2) {
      open = false;
      results = { doctors: [], specialties: [], conditions: [] };
      return;
    }
    debounceTimer = setTimeout(() => fetchSuggestions(term), 250);
  }

  async function fetchSuggestions(term: string) {
    controller?.abort();
    controller = new AbortController();
    try {
      const res = await fetch(`/api/autocomplete?q=${encodeURIComponent(term)}`, { signal: controller.signal });
      if (!res.ok) { open = false; return; }
      const data = await res.json();
      results = {
        doctors: data.doctors ?? [],
        specialties: data.specialties ?? [],
        conditions: data.conditions ?? [],
      };
      highlighted = -1;
      open = true;
    } catch (e) {
      if ((e as Error)?.name !== "AbortError") open = false;
    }
  }

  function select(href: string) {
    open = false;
    goto(href);
  }

  async function submit(event: Event) {
    event.preventDefault();
    if (open && highlighted >= 0 && highlighted < flat.length) {
      select(flat[highlighted]);
      return;
    }
    const q = value.trim();
    open = false;
    if (!q) { goto(href("/doctors")); return; }
    try {
      const res = await fetch(`/api/search/resolve?q=${encodeURIComponent(q)}`);
      const r = res.ok ? await res.json() : { type: "query", slug: null, label: q };
      if (r.type === "specialty") goto(specialtyHref(r.slug));
      else if (r.type === "condition") goto(conditionHref(r.slug));
      else goto(mapMode ? href("/doctors/map") + `?q=${encodeURIComponent(q)}` : href("/doctors") + `?q=${encodeURIComponent(q)}`);
    } catch {
      goto(href("/doctors") + `?q=${encodeURIComponent(q)}`);
    }
  }

  function onKeydown(event: KeyboardEvent) {
    if (!open) return;
    if (event.key === "Escape") {
      open = false;
      return;
    }
    if (flat.length === 0) return;
    if (event.key === "ArrowDown") {
      event.preventDefault();
      highlighted = (highlighted + 1) % flat.length;
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      highlighted = (highlighted - 1 + flat.length) % flat.length;
    }
  }

  $effect(() => {
    function onDocPointerDown(e: PointerEvent) {
      if (wrapper && !wrapper.contains(e.target as Node)) open = false;
    }
    document.addEventListener("pointerdown", onDocPointerDown);
    return () => document.removeEventListener("pointerdown", onDocPointerDown);
  });
</script>

<div class="search-wrap" bind:this={wrapper}>
  <form class="search" onsubmit={submit}>
    <span class="search-icon">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="7" />
        <line x1="16.5" y1="16.5" x2="21" y2="21" />
      </svg>
    </span>
    <input
      type="text"
      {placeholder}
      bind:value
      oninput={onInput}
      onkeydown={onKeydown}
      onfocus={() => { if (hasResults) open = true; }}
      autofocus={autofocus}
      role="combobox"
      aria-expanded={open}
      aria-controls="search-suggestions"
      aria-autocomplete="list"
      aria-label={m.search_aria()}
    />
    <button type="submit" class="search-btn">{m.search_button()}</button>
  </form>

  {#if open && value.trim().length >= 2}
    <div class="suggestions" id="search-suggestions" role="listbox">
      {#if hasResults}
        {#if results.doctors.length > 0}
          <div class="group-header">{m.search_group_doctors()}</div>
          {#each results.doctors as d, i (d.slug)}
            <button
              type="button"
              class="suggestion"
              class:highlighted={highlighted === i}
              role="option"
              aria-selected={highlighted === i}
              onmouseenter={() => (highlighted = i)}
              onclick={() => select(href(`/doctors/${d.slug}`))}>
              <span class="label">{localizedField(d.fullNameKa, d.fullNameEn, getLocale())}</span>
              {#if d.primarySpecialtyEn || d.primarySpecialtyKa}<span class="sub">{localizedField(d.primarySpecialtyKa, d.primarySpecialtyEn, getLocale())}</span>{/if}
            </button>
          {/each}
        {/if}
        {#if results.specialties.length > 0}
          <div class="group-header">{m.search_group_specialties()}</div>
          {#each results.specialties as s, j (s.slug)}
            <button
              type="button"
              class="suggestion"
              class:highlighted={highlighted === results.doctors.length + j}
              role="option"
              aria-selected={highlighted === results.doctors.length + j}
              onmouseenter={() => (highlighted = results.doctors.length + j)}
              onclick={() => select(specialtyHref(s.slug))}>
              <span class="label">{localizedField(s.nameKa, s.nameEn, getLocale())}</span>
              <span class="sub">{countLabel(s.doctorCount)}</span>
            </button>
          {/each}
        {/if}
        {#if results.conditions.length > 0}
          <div class="group-header">{m.search_group_conditions()}</div>
          {#each results.conditions as c, k (c.slug)}
            <button
              type="button"
              class="suggestion"
              class:highlighted={highlighted === results.doctors.length + results.specialties.length + k}
              role="option"
              aria-selected={highlighted === results.doctors.length + results.specialties.length + k}
              onmouseenter={() => (highlighted = results.doctors.length + results.specialties.length + k)}
              onclick={() => select(conditionHref(c.slug))}>
              <span class="label">{localizedField(c.nameKa, c.nameEn, getLocale())}</span>
              <span class="sub">{countLabel(c.doctorCount)}</span>
            </button>
          {/each}
        {/if}
      {:else}
        <div class="no-matches">{m.search_no_matches()}</div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .search-wrap { position: relative; }
  .search {
    display: flex;
    align-items: stretch;
    background: var(--surface);
    border: 1px solid var(--line-strong);
    border-radius: 10px;
    overflow: hidden;
    transition: border-color 0.15s, box-shadow 0.15s;
    box-shadow: 0 1px 2px rgba(14, 19, 32, 0.04);
  }
  .search:focus-within {
    border-color: var(--accent);
    box-shadow: 0 0 0 4px var(--accent-soft);
  }
  .search-icon {
    display: flex;
    align-items: center;
    padding-left: 1.1rem;
    color: var(--ink-faint);
  }
  input {
    flex: 1;
    border: none;
    outline: none;
    background: transparent;
    font-size: 1.05rem;
    color: var(--ink);
    padding: 1.1rem 1rem;
    min-width: 0;
  }
  input::placeholder { color: var(--ink-faint); }
  .search-btn {
    border: none;
    background: var(--accent);
    color: white;
    padding: 0 1.6rem;
    font-size: 0.92rem;
    font-weight: 600;
    transition: background 0.15s;
    white-space: nowrap;
  }
  .search-btn:hover { background: var(--accent-deep); }

  .suggestions {
    position: absolute;
    top: calc(100% + 0.4rem);
    left: 0;
    right: 0;
    z-index: 60;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 10px;
    box-shadow: 0 8px 24px rgba(14, 19, 32, 0.12);
    overflow: hidden;
    text-align: left;
  }
  .group-header {
    padding: 0.5rem 1rem 0.3rem;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--ink-faint);
  }
  .suggestion {
    display: flex;
    align-items: baseline;
    gap: 0.6rem;
    width: 100%;
    padding: 0.6rem 1rem;
    border: 0;
    background: none;
    cursor: pointer;
    text-align: left;
    font: inherit;
    color: var(--ink);
  }
  .suggestion.highlighted { background: var(--accent-soft); }
  .suggestion .label { font-weight: 500; }
  .suggestion .sub { color: var(--ink-muted); font-size: 0.85rem; margin-left: auto; }
  .no-matches { padding: 0.8rem 1rem; color: var(--ink-muted); font-size: 0.9rem; }
</style>
