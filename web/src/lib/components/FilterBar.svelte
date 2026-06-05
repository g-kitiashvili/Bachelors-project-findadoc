<script lang="ts">
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  import * as m from "$lib/paraglide/messages";
  import { localizedField } from "$lib/i18n";
  import { getLocale } from "$lib/paraglide/runtime";
  import FilterDrawer from "./FilterDrawer.svelte";

  interface SpecialtyOption { slug: string; nameKa: string; nameEn: string; doctorCount: number; parentSlug?: string | null }
  interface ClinicOption { slug: string; nameKa: string; nameEn: string; doctorCount: number }
  interface LocationCity { slug: string; nameKa: string; nameEn: string; doctorCount: number }
  interface LocationRegion extends LocationCity { cities: LocationCity[] }

  interface Props {
    selectedSlugs: string[];
    specialties: SpecialtyOption[];
    regions: LocationRegion[];
    selectedRegion: string;
    selectedCity: string;
    clinics: ClinicOption[];
    selectedClinics: string[];
    selectedTreatsChildren: boolean;
    selectedTreatsAdults: boolean;
  }

  let { selectedSlugs, specialties, regions, selectedRegion, selectedCity, clinics, selectedClinics, selectedTreatsChildren, selectedTreatsAdults }: Props = $props();

  let drawerOpen = $state(false);

  const selectedSpecialties = $derived(
    selectedSlugs
      .map((slug) => specialties.find((s) => s.slug === slug))
      .filter((s): s is SpecialtyOption => s !== undefined)
  );

  const selectedClinicOptions = $derived(
    selectedClinics
      .map((slug) => clinics.find((c) => c.slug === slug))
      .filter((c): c is ClinicOption => c !== undefined)
  );

  const regionLabel = $derived.by(() => {
    const r = regions.find((r) => r.slug === selectedRegion);
    return r ? localizedField(r.nameKa, r.nameEn, getLocale()) : "";
  });
  const cityLabel = $derived.by(() => {
    const c = regions.flatMap((r) => r.cities).find((c) => c.slug === selectedCity);
    return c ? localizedField(c.nameKa, c.nameEn, getLocale()) : "";
  });

  function removeSlug(slug: string) {
    const next = selectedSlugs.filter((s) => s !== slug);
    const url = new URL($page.url);
    if (next.length > 0) {
      url.searchParams.set("specialty", next.join(","));
    } else {
      url.searchParams.delete("specialty");
    }
    url.searchParams.delete("page");
    goto(url.pathname + url.search);
  }

  function removeClinic(slug: string) {
    const next = selectedClinics.filter((s) => s !== slug);
    const url = new URL($page.url);
    if (next.length > 0) {
      url.searchParams.set("clinic", next.join(","));
    } else {
      url.searchParams.delete("clinic");
    }
    url.searchParams.delete("page");
    goto(url.pathname + url.search);
  }

  function clearLocation(kind: "region" | "city") {
    const url = new URL($page.url);
    if (kind === "region") { url.searchParams.delete("region"); url.searchParams.delete("city"); }
    else url.searchParams.delete("city");
    url.searchParams.delete("page");
    goto(url.pathname + url.search);
  }

  function clearTreats(kind: "children" | "adults") {
    const url = new URL($page.url);
    url.searchParams.delete(kind === "children" ? "treatsChildren" : "treatsAdults");
    url.searchParams.delete("page");
    goto(url.pathname + url.search);
  }

  function clearAll() {
    const url = new URL($page.url);
    url.searchParams.delete("specialty");
    url.searchParams.delete("region");
    url.searchParams.delete("city");
    url.searchParams.delete("clinic");
    url.searchParams.delete("treatsChildren");
    url.searchParams.delete("treatsAdults");
    url.searchParams.delete("page");
    goto(url.pathname + url.search);
  }
</script>

<div class="bar">
  <button class="filters-btn" onclick={() => (drawerOpen = true)}>
    <span>{m.filter_filters()}{selectedSlugs.length > 0 ? ` (${selectedSlugs.length})` : ""}</span>
  </button>

  <div class="chips">
    {#each selectedSpecialties as s (s.slug)}
      {@const label = localizedField(s.nameKa, s.nameEn, getLocale())}
      <button class="chip" onclick={() => removeSlug(s.slug)} aria-label={m.filter_remove_aria({ label })}>
        <span>{label}</span>
        <span class="x">✕</span>
      </button>
    {/each}
    {#if regionLabel}
      <button class="chip" onclick={() => clearLocation("region")} aria-label={m.filter_remove_aria({ label: regionLabel })}>
        <span>{regionLabel}</span><span class="x">✕</span>
      </button>
    {/if}
    {#if cityLabel}
      <button class="chip" onclick={() => clearLocation("city")} aria-label={m.filter_remove_aria({ label: cityLabel })}>
        <span>{cityLabel}</span><span class="x">✕</span>
      </button>
    {/if}
    {#each selectedClinicOptions as c (c.slug)}
      {@const label = localizedField(c.nameKa, c.nameEn, getLocale())}
      <button class="chip" onclick={() => removeClinic(c.slug)} aria-label={m.filter_remove_aria({ label })}>
        <span>{label}</span>
        <span class="x">✕</span>
      </button>
    {/each}
    {#if selectedTreatsChildren}
      <button class="chip" onclick={() => clearTreats("children")} aria-label={m.filter_remove_aria({ label: m.filter_treats_children() })}>
        <span>{m.filter_treats_children()}</span>
        <span class="x">✕</span>
      </button>
    {/if}
    {#if selectedTreatsAdults}
      <button class="chip" onclick={() => clearTreats("adults")} aria-label={m.filter_remove_aria({ label: m.filter_treats_adults() })}>
        <span>{m.filter_treats_adults()}</span>
        <span class="x">✕</span>
      </button>
    {/if}
  </div>

  {#if selectedSlugs.length > 0 || regionLabel || cityLabel || selectedClinics.length > 0 || selectedTreatsChildren || selectedTreatsAdults}
    <button class="clear" onclick={clearAll}>{m.filter_clear_all()}</button>
  {/if}
</div>

<FilterDrawer
  open={drawerOpen}
  {selectedSlugs}
  {specialties}
  onClose={() => (drawerOpen = false)}
  {regions}
  {selectedRegion}
  {selectedCity}
  {clinics}
  {selectedClinics}
  {selectedTreatsChildren}
  {selectedTreatsAdults}
/>

<style>
  .bar { max-width: 1280px; margin: 1.5rem auto 0; padding: 0 2rem; display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap; }
  .filters-btn { background: white; border: 1px solid var(--line); padding: 0.55rem 1rem; border-radius: 100px; font: inherit; cursor: pointer; display: inline-flex; align-items: center; gap: 0.5rem; }
  .filters-btn::before { content: "≡"; font-weight: bold; }
  .filters-btn:hover { border-color: var(--accent); color: var(--accent); }
  .chips { display: flex; gap: 0.5rem; flex-wrap: wrap; flex: 1; }
  .chip { display: inline-flex; align-items: center; gap: 0.4rem; background: var(--bg-soft); border: 1px solid var(--line); border-radius: 100px; padding: 0.4rem 0.85rem; font: inherit; font-size: 0.86rem; cursor: pointer; color: var(--ink); }
  .chip:hover { background: white; border-color: var(--accent); }
  .chip .x { color: var(--ink-muted); font-size: 0.8rem; }
  .clear { background: none; border: 0; color: var(--accent); font: inherit; font-size: 0.86rem; cursor: pointer; }
  .clear:hover { text-decoration: underline; }
</style>
