<script lang="ts">
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  import { untrack } from "svelte";

  interface LocationCity { slug: string; nameKa: string; nameEn: string; doctorCount: number }
  interface LocationRegion extends LocationCity { cities: LocationCity[] }

  interface Props {
    open: boolean;
    selectedSlugs: string[];
    specialties: Array<{ slug: string; nameEn: string; nameKa: string; doctorCount: number }>;
    onClose: () => void;
    regions: LocationRegion[];
    selectedRegion: string;
    selectedCity: string;
    clinics: Array<{ slug: string; nameKa: string; nameEn: string; doctorCount: number }>;
    selectedClinics: string[];
  }

  let { open, selectedSlugs, specialties, onClose, regions, selectedRegion, selectedCity, clinics, selectedClinics }: Props = $props();

  let draft = $state<string[]>([...selectedSlugs]);
  let search = $state("");
  let regionDraft = $state(selectedRegion);
  let cityDraft = $state(selectedCity);
  let liveSpecialties = $state<Props["specialties"]>([...specialties]);
  let nameBySlug = $state<Record<string, { nameEn: string; nameKa: string }>>(
    Object.fromEntries(specialties.map((s) => [s.slug, { nameEn: s.nameEn, nameKa: s.nameKa }]))
  );

  let clinicDraft = $state<string[]>([...selectedClinics]);
  let clinicSearch = $state("");
  let liveClinics = $state<Props["clinics"]>([...clinics]);
  let clinicNameBySlug = $state<Record<string, { nameEn: string; nameKa: string }>>(
    Object.fromEntries(clinics.map((c) => [c.slug, { nameEn: c.nameEn, nameKa: c.nameKa }]))
  );

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

  $effect(() => {
    draft = [...selectedSlugs];
  });

  $effect(() => {
    clinicDraft = [...selectedClinics];
  });

  $effect(() => { regionDraft = selectedRegion; });
  $effect(() => { cityDraft = selectedCity; });

  $effect(() => {
    if (
      regionDraft === selectedRegion &&
      cityDraft === selectedCity &&
      clinicDraft.join(",") === selectedClinics.join(",")
    ) {
      liveSpecialties = [...specialties];
      rememberNames(specialties);
      return;
    }
    const params = new URLSearchParams();
    if (regionDraft) params.set("region", regionDraft);
    if (cityDraft) params.set("city", cityDraft);
    if (clinicDraft.length > 0) params.set("clinic", clinicDraft.join(","));
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

  const withSelected = $derived.by(() => {
    const present = new Set(liveSpecialties.map((s) => s.slug));
    const extras = draft
      .filter((slug) => !present.has(slug))
      .map((slug) => ({
        slug,
        nameEn: nameBySlug[slug]?.nameEn ?? slug,
        nameKa: nameBySlug[slug]?.nameKa ?? "",
        doctorCount: 0,
      }));
    return [...liveSpecialties, ...extras];
  });

  const filtered = $derived(
    search.trim() === ""
      ? withSelected
      : withSelected.filter((s) =>
          s.nameEn.toLowerCase().includes(search.toLowerCase()) ||
          s.nameKa.includes(search)
        )
  );

  let liveRegions = $state<LocationRegion[]>([...regions]);

  $effect(() => {
    if (draft.length === 0 && clinicDraft.length === 0) {
      liveRegions = [...regions];
      return;
    }
    const params = new URLSearchParams();
    if (draft.length > 0) params.set("specialty", draft.join(","));
    if (clinicDraft.length > 0) params.set("clinic", clinicDraft.join(","));
    let cancelled = false;
    fetch(`/api/locations?${params.toString()}`)
      .then((r) => (r.ok ? r.json() : { items: [] }))
      .then((d: { items: LocationRegion[] }) => {
        if (!cancelled) liveRegions = d.items ?? [];
      })
      .catch(() => {});
    return () => { cancelled = true; };
  });

  const cityOptions = $derived(
    liveRegions.find((r) => r.slug === regionDraft)?.cities ?? []
  );

  $effect(() => {
    if (
      regionDraft === selectedRegion &&
      cityDraft === selectedCity &&
      draft.join(",") === selectedSlugs.join(",")
    ) {
      liveClinics = [...clinics];
      rememberClinicNames(clinics);
      return;
    }
    const params = new URLSearchParams();
    if (regionDraft) params.set("region", regionDraft);
    if (cityDraft) params.set("city", cityDraft);
    if (draft.length > 0) params.set("specialty", draft.join(","));
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

  const withSelectedClinics = $derived.by(() => {
    const present = new Set(liveClinics.map((c) => c.slug));
    const extras = clinicDraft
      .filter((slug) => !present.has(slug))
      .map((slug) => ({
        slug,
        nameEn: clinicNameBySlug[slug]?.nameEn ?? slug,
        nameKa: clinicNameBySlug[slug]?.nameKa ?? "",
        doctorCount: 0,
      }));
    return [...liveClinics, ...extras];
  });

  const filteredClinics = $derived(
    clinicSearch.trim() === ""
      ? withSelectedClinics
      : withSelectedClinics.filter((c) =>
          c.nameEn.toLowerCase().includes(clinicSearch.toLowerCase()) ||
          c.nameKa.includes(clinicSearch)
        )
  );

  function toggle(slug: string) {
    if (draft.includes(slug)) {
      draft = draft.filter((s) => s !== slug);
    } else {
      draft = [...draft, slug];
    }
  }

  function toggleClinic(slug: string) {
    if (clinicDraft.includes(slug)) {
      clinicDraft = clinicDraft.filter((s) => s !== slug);
    } else {
      clinicDraft = [...clinicDraft, slug];
    }
  }

  function onRegionChange(value: string) {
    regionDraft = value;
    cityDraft = "";
  }

  function apply() {
    const url = new URL($page.url);
    if (draft.length > 0) {
      url.searchParams.set("specialty", draft.join(","));
    } else {
      url.searchParams.delete("specialty");
    }
    if (regionDraft) url.searchParams.set("region", regionDraft);
    else url.searchParams.delete("region");
    if (cityDraft) url.searchParams.set("city", cityDraft);
    else url.searchParams.delete("city");
    if (clinicDraft.length > 0) url.searchParams.set("clinic", clinicDraft.join(","));
    else url.searchParams.delete("clinic");
    url.searchParams.delete("page");
    goto(url.pathname + url.search);
    onClose();
  }

  function clearDraft() {
    draft = [];
    regionDraft = "";
    cityDraft = "";
    clinicDraft = [];
  }
</script>

{#if open}
  <div class="backdrop" onclick={onClose} role="presentation"></div>
  <aside class="drawer" role="dialog" aria-label="Filters">
    <header>
      <h2>Filters</h2>
      <button class="close" onclick={onClose} aria-label="Close">✕</button>
    </header>

    <div class="section">
      <div class="label">Region</div>
      <select class="search" value={regionDraft} onchange={(e) => onRegionChange(e.currentTarget.value)}>
        <option value="">All regions</option>
        {#each liveRegions as r (r.slug)}
          <option value={r.slug}>{r.nameEn} ({r.doctorCount})</option>
        {/each}
      </select>

      {#if cityOptions.length > 0}
        <div class="label" style="margin-top:0.75rem;">City</div>
        <select class="search" bind:value={cityDraft}>
          <option value="">All cities</option>
          {#each cityOptions as c (c.slug)}
            <option value={c.slug}>{c.nameEn} ({c.doctorCount})</option>
          {/each}
        </select>
      {/if}
    </div>

    <div class="section">
      <div class="label">Specialty</div>
      <input
        class="search"
        type="text"
        placeholder="Search specialties..."
        bind:value={search}
      />
      <ul class="checklist">
        {#each filtered as s (s.slug)}
          <li>
            <label>
              <input
                type="checkbox"
                checked={draft.includes(s.slug)}
                onchange={() => toggle(s.slug)}
              />
              <span class="name">{s.nameEn}</span>
              <span class="count">({s.doctorCount})</span>
            </label>
          </li>
        {/each}
      </ul>
    </div>

    <div class="section">
      <div class="label">Clinic</div>
      <input
        class="search"
        type="text"
        placeholder="Search clinics..."
        bind:value={clinicSearch}
      />
      <ul class="checklist">
        {#each filteredClinics as c (c.slug)}
          <li>
            <label>
              <input
                type="checkbox"
                checked={clinicDraft.includes(c.slug)}
                onchange={() => toggleClinic(c.slug)}
              />
              <span class="name">{c.nameEn}</span>
              <span class="count">({c.doctorCount})</span>
            </label>
          </li>
        {/each}
      </ul>
    </div>

    <footer>
      <button class="apply" onclick={apply}>Apply</button>
      <button class="clear" onclick={clearDraft}>Clear</button>
    </footer>
  </aside>
{/if}

<style>
  .backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.35); z-index: 40; }
  .drawer { position: fixed; top: 0; left: 0; bottom: 0; width: 360px; background: white; z-index: 50; display: flex; flex-direction: column; box-shadow: 2px 0 16px rgba(0,0,0,0.1); }
  header { display: flex; justify-content: space-between; align-items: center; padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--line); }
  header h2 { font-family: var(--display); font-size: 1.25rem; margin: 0; }
  .close { background: none; border: 0; font-size: 1.25rem; cursor: pointer; color: var(--ink-muted); }
  .section { flex: 1; overflow-y: auto; padding: 1.25rem 1.5rem; }
  .label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--ink-muted); margin-bottom: 0.75rem; }
  .search { width: 100%; padding: 0.55rem 0.75rem; border: 1px solid var(--line); border-radius: 6px; margin-bottom: 0.75rem; font: inherit; }
  .checklist { list-style: none; margin: 0; padding: 0; }
  .checklist li { margin-bottom: 0.4rem; }
  .checklist label { display: flex; gap: 0.6rem; align-items: center; cursor: pointer; font-size: 0.9rem; }
  .checklist .name { flex: 1; }
  .checklist .count { color: var(--ink-faint); font-size: 0.8rem; }
  footer { display: flex; gap: 0.75rem; padding: 1.25rem 1.5rem; border-top: 1px solid var(--line); }
  .apply { flex: 1; background: var(--accent); color: white; border: 0; padding: 0.7rem; border-radius: 6px; font: inherit; font-weight: 600; cursor: pointer; }
  .clear { background: none; border: 1px solid var(--line); padding: 0.7rem 1rem; border-radius: 6px; font: inherit; cursor: pointer; color: var(--ink); }
</style>
