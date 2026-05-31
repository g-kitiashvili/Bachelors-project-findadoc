<script lang="ts">
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  import { untrack } from "svelte";
  import * as m from "$lib/paraglide/messages";
  import { localizedField } from "$lib/i18n";
  import { getLocale } from "$lib/paraglide/runtime";
  import MultiSelect from "./MultiSelect.svelte";

  interface LocationCity { slug: string; nameKa: string; nameEn: string; doctorCount: number }
  interface LocationRegion extends LocationCity { cities: LocationCity[] }

  interface Props {
    open: boolean;
    selectedSlugs: string[];
    specialties: Array<{ slug: string; nameEn: string; nameKa: string; doctorCount: number; parentSlug?: string | null }>;
    onClose: () => void;
    regions: LocationRegion[];
    selectedRegion: string;
    selectedCity: string;
    clinics: Array<{ slug: string; nameKa: string; nameEn: string; doctorCount: number }>;
    selectedClinics: string[];
    selectedTreatsChildren: boolean;
    selectedTreatsAdults: boolean;
  }

  let { open, selectedSlugs, specialties, onClose, regions, selectedRegion, selectedCity, clinics, selectedClinics, selectedTreatsChildren, selectedTreatsAdults }: Props = $props();

  let draft = $state<string[]>([...selectedSlugs]);
  let regionDraft = $state(selectedRegion);
  let cityDraft = $state(selectedCity);
  let liveSpecialties = $state<Props["specialties"]>([...specialties]);
  let nameBySlug = $state<Record<string, { nameEn: string; nameKa: string }>>(
    Object.fromEntries(specialties.map((s) => [s.slug, { nameEn: s.nameEn, nameKa: s.nameKa }]))
  );

  let clinicDraft = $state<string[]>([...selectedClinics]);
  let liveClinics = $state<Props["clinics"]>([...clinics]);
  let clinicNameBySlug = $state<Record<string, { nameEn: string; nameKa: string }>>(
    Object.fromEntries(clinics.map((c) => [c.slug, { nameEn: c.nameEn, nameKa: c.nameKa }]))
  );

  let treatsChildrenDraft = $state(selectedTreatsChildren);
  let treatsAdultsDraft = $state(selectedTreatsAdults);

  function rememberNames(items: Props["specialties"]) {
    const acc = { ...untrack(() => nameBySlug) };
    for (const s of items) acc[s.slug] = { nameEn: s.nameEn, nameKa: s.nameKa };
    nameBySlug = acc;
  }

  function rememberClinicNames(items: Props["clinics"]) {
    const acc = { ...untrack(() => clinicNameBySlug) };
    for (const c of items) acc[c.slug] = { nameEn: c.nameEn, nameKa: c.nameKa };
    clinicNameBySlug = acc;
  }

  $effect(() => { draft = [...selectedSlugs]; });
  $effect(() => { clinicDraft = [...selectedClinics]; });
  $effect(() => { regionDraft = selectedRegion; });
  $effect(() => { cityDraft = selectedCity; });
  $effect(() => { treatsChildrenDraft = selectedTreatsChildren; });
  $effect(() => { treatsAdultsDraft = selectedTreatsAdults; });

  $effect(() => {
    if (
      regionDraft === selectedRegion &&
      cityDraft === selectedCity &&
      clinicDraft.join(",") === selectedClinics.join(",") &&
      treatsChildrenDraft === selectedTreatsChildren &&
      treatsAdultsDraft === selectedTreatsAdults
    ) {
      liveSpecialties = [...specialties];
      rememberNames(specialties);
      return;
    }
    const params = new URLSearchParams();
    if (regionDraft) params.set("region", regionDraft);
    if (cityDraft) params.set("city", cityDraft);
    if (clinicDraft.length > 0) params.set("clinic", clinicDraft.join(","));
    if (treatsChildrenDraft) params.set("treats_children", "true");
    if (treatsAdultsDraft) params.set("treats_adults", "true");
    let cancelled = false;
    fetch(`/api/specialties?${params.toString()}`)
      .then((r) => (r.ok ? r.json() : { items: [] }))
      .then((d: { items: Props["specialties"] }) => {
        if (cancelled) return;
        const items = (d.items ?? []).filter((s) => s.doctorCount > 0);
        liveSpecialties = items;
        rememberNames(items);
      })
      .catch(() => {});
    return () => { cancelled = true; };
  });

  const specialtyOptions = $derived.by(() => {
    const present = new Set(liveSpecialties.map((s) => s.slug));
    const extras = draft
      .filter((slug) => !present.has(slug))
      .map((slug) => ({ slug, nameEn: nameBySlug[slug]?.nameEn ?? slug, nameKa: nameBySlug[slug]?.nameKa ?? "", doctorCount: 0 }));
    return [...liveSpecialties, ...extras].map((s) => {
      const name = localizedField(s.nameKa, s.nameEn, getLocale()) || s.slug;
      return {
        value: s.slug,
        label: ("parentSlug" in s && s.parentSlug) ? `↳ ${name}` : name,
        count: s.doctorCount,
      };
    });
  });

  let liveRegions = $state<LocationRegion[]>([...regions]);

  $effect(() => {
    if (draft.length === 0 && clinicDraft.length === 0 && treatsChildrenDraft === selectedTreatsChildren && treatsAdultsDraft === selectedTreatsAdults) {
      liveRegions = [...regions];
      return;
    }
    const params = new URLSearchParams();
    if (draft.length > 0) params.set("specialty", draft.join(","));
    if (clinicDraft.length > 0) params.set("clinic", clinicDraft.join(","));
    if (treatsChildrenDraft) params.set("treats_children", "true");
    if (treatsAdultsDraft) params.set("treats_adults", "true");
    let cancelled = false;
    fetch(`/api/locations?${params.toString()}`)
      .then((r) => (r.ok ? r.json() : { items: [] }))
      .then((d: { items: LocationRegion[] }) => {
        if (!cancelled) liveRegions = d.items ?? [];
      })
      .catch(() => {});
    return () => { cancelled = true; };
  });

  const cityList = $derived(liveRegions.find((r) => r.slug === regionDraft)?.cities ?? []);

  const regionOptions = $derived([
    { value: "", label: m.drawer_all_regions() },
    ...liveRegions.map((r) => ({ value: r.slug, label: localizedField(r.nameKa, r.nameEn, getLocale()), count: r.doctorCount })),
  ]);
  const cityOptions = $derived([
    { value: "", label: m.drawer_all_cities() },
    ...cityList.map((c) => ({ value: c.slug, label: localizedField(c.nameKa, c.nameEn, getLocale()), count: c.doctorCount })),
  ]);

  $effect(() => {
    if (
      regionDraft === selectedRegion &&
      cityDraft === selectedCity &&
      draft.join(",") === selectedSlugs.join(",") &&
      treatsChildrenDraft === selectedTreatsChildren &&
      treatsAdultsDraft === selectedTreatsAdults
    ) {
      liveClinics = [...clinics];
      rememberClinicNames(clinics);
      return;
    }
    const params = new URLSearchParams();
    if (regionDraft) params.set("region", regionDraft);
    if (cityDraft) params.set("city", cityDraft);
    if (draft.length > 0) params.set("specialty", draft.join(","));
    if (treatsChildrenDraft) params.set("treats_children", "true");
    if (treatsAdultsDraft) params.set("treats_adults", "true");
    let cancelled = false;
    fetch(`/api/clinics?${params.toString()}`)
      .then((r) => (r.ok ? r.json() : { items: [] }))
      .then((d: { items: Props["clinics"] }) => {
        if (cancelled) return;
        const items = (d.items ?? []).filter((c) => c.doctorCount > 0);
        liveClinics = items;
        rememberClinicNames(items);
      })
      .catch(() => {});
    return () => { cancelled = true; };
  });

  const clinicOptions = $derived.by(() => {
    const present = new Set(liveClinics.map((c) => c.slug));
    const extras = clinicDraft
      .filter((slug) => !present.has(slug))
      .map((slug) => ({ slug, nameEn: clinicNameBySlug[slug]?.nameEn ?? slug, nameKa: clinicNameBySlug[slug]?.nameKa ?? "", doctorCount: 0 }));
    return [...liveClinics, ...extras].map((c) => ({ value: c.slug, label: localizedField(c.nameKa, c.nameEn, getLocale()) || c.slug, count: c.doctorCount }));
  });

  function onRegionChange(value: string) {
    regionDraft = value;
    cityDraft = "";
  }

  function apply() {
    const url = new URL($page.url);
    if (draft.length > 0) url.searchParams.set("specialty", draft.join(","));
    else url.searchParams.delete("specialty");
    if (regionDraft) url.searchParams.set("region", regionDraft);
    else url.searchParams.delete("region");
    if (cityDraft) url.searchParams.set("city", cityDraft);
    else url.searchParams.delete("city");
    if (clinicDraft.length > 0) url.searchParams.set("clinic", clinicDraft.join(","));
    else url.searchParams.delete("clinic");
    if (treatsChildrenDraft) url.searchParams.set("treats_children", "true");
    else url.searchParams.delete("treats_children");
    if (treatsAdultsDraft) url.searchParams.set("treats_adults", "true");
    else url.searchParams.delete("treats_adults");
    url.searchParams.delete("page");
    goto(url.pathname + url.search);
    onClose();
  }

  function clearDraft() {
    draft = [];
    regionDraft = "";
    cityDraft = "";
    clinicDraft = [];
    treatsChildrenDraft = false;
    treatsAdultsDraft = false;
  }
</script>

{#if open}
  <div class="backdrop" onclick={onClose} role="presentation"></div>
  <aside class="drawer" role="dialog" aria-label={m.filter_filters()}>
    <header>
      <h2>{m.filter_filters()}</h2>
      <button class="close" onclick={onClose} aria-label={m.drawer_close()}>✕</button>
    </header>

    <div class="body">
      <MultiSelect
        label={m.drawer_specialty()}
        placeholder={m.drawer_select_specialty()}
        searchPlaceholder={m.drawer_search_specialties()}
        options={specialtyOptions}
        selected={draft}
        onChange={(next) => (draft = next)}
      />

      <MultiSelect
        label={m.drawer_region()}
        placeholder={m.drawer_all_regions()}
        multiple={false}
        options={regionOptions}
        selected={regionDraft ? [regionDraft] : []}
        onChange={(next) => onRegionChange(next[0] ?? "")}
      />

      {#if cityList.length > 0}
        <MultiSelect
          label={m.drawer_city()}
          placeholder={m.drawer_all_cities()}
          multiple={false}
          searchable={false}
          options={cityOptions}
          selected={cityDraft ? [cityDraft] : []}
          onChange={(next) => (cityDraft = next[0] ?? "")}
        />
      {/if}

      <MultiSelect
        label={m.drawer_clinic()}
        placeholder={m.drawer_select_clinic()}
        searchPlaceholder={m.drawer_search_clinics()}
        options={clinicOptions}
        selected={clinicDraft}
        onChange={(next) => (clinicDraft = next)}
      />

      <div class="agegroup">
        <span class="ag-label">{m.drawer_patients()}</span>
        <label><input type="checkbox" bind:checked={treatsChildrenDraft} /> {m.filter_treats_children()}</label>
        <label><input type="checkbox" bind:checked={treatsAdultsDraft} /> {m.filter_treats_adults()}</label>
      </div>
    </div>

    <footer>
      <button class="clear" onclick={clearDraft}>{m.drawer_clear()}</button>
      <button class="apply" onclick={apply}>{m.drawer_apply()}</button>
    </footer>
  </aside>
{/if}

<style>
  .backdrop { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.35); z-index: 40; }
  .drawer {
    position: fixed; top: 0; left: 0; bottom: 0; width: min(360px, 90vw); background: white; z-index: 50;
    display: flex; flex-direction: column; box-shadow: 2px 0 16px rgba(0, 0, 0, 0.1);
  }
  header { display: flex; justify-content: space-between; align-items: center; padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--line); }
  header h2 { font-family: var(--display); font-size: 1.25rem; margin: 0; }
  .close { background: none; border: 0; font-size: 1.25rem; cursor: pointer; color: var(--ink-muted); }
  .body { flex: 1 1 auto; overflow: visible; padding: 1.5rem; display: flex; flex-direction: column; gap: 1.1rem; }
  footer { display: flex; gap: 0.75rem; padding: 1.25rem 1.5rem; border-top: 1px solid var(--line); }
  .apply { flex: 1; background: var(--accent); color: white; border: 0; padding: 0.7rem; border-radius: 8px; font: inherit; font-weight: 600; cursor: pointer; }
  .apply:hover { background: var(--accent-deep); }
  .clear { background: none; border: 1px solid var(--line); padding: 0.7rem 1rem; border-radius: 8px; font: inherit; cursor: pointer; color: var(--ink); }
  .clear:hover { border-color: var(--line-strong); }
  .agegroup { display: flex; flex-direction: column; gap: 0.4rem; }
  .ag-label { font-size: 0.8rem; font-weight: 600; color: var(--ink-muted); }
  .agegroup label { display: flex; gap: 0.5rem; align-items: center; font-size: 0.92rem; cursor: pointer; }
</style>
