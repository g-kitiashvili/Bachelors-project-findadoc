<script lang="ts">
  import DoctorCard from "$lib/components/DoctorCard.svelte";
  import FilterBar from "$lib/components/FilterBar.svelte";
  import Pagination from "$lib/components/Pagination.svelte";
  import SearchBar from "$lib/components/SearchBar.svelte";
  import SortSelect from "$lib/components/SortSelect.svelte";

  let { data } = $props();

  const hasQuery = $derived(Boolean(data.q));
  const headlineMain = $derived(
    !hasQuery
      ? data.total > 0
        ? `${data.total} doctors`
        : "Doctors"
      : data.total > 0
        ? `${data.total} ${data.total === 1 ? "result" : "results"}`
        : "No matches",
  );
  const headlineSub = $derived(
    hasQuery
      ? `For "${data.q}"`
      : "Verified profiles, indexed daily from public sources.",
  );
</script>

<svelte:head>
  <title>{hasQuery ? `Search · ${data.q}` : "Doctors"} — Find-a-Doc</title>
</svelte:head>

<div class="search-strip">
  <div class="search-strip-inner">
    <SearchBar initialValue={data.q ?? ""} />
    {#if hasQuery}
      <a class="clear" href="/doctors">Clear search</a>
    {/if}
  </div>
</div>

<FilterBar selectedSlugs={data.selectedSlugs} specialties={data.specialties} regions={data.regions} selectedRegion={data.selectedRegion} selectedCity={data.selectedCity} clinics={data.clinics} selectedClinics={data.selectedClinics} />

<div class="section-head">
  <div>
    <h1>{headlineMain}</h1>
    <p>{headlineSub}</p>
  </div>
  <div class="meta">
    <SortSelect value={data.selectedSort} hasQuery={hasQuery} />
    {#if data.total > 0}
      <span class="page-indicator">Page {data.page} · {data.pageSize} per page</span>
    {/if}
  </div>
</div>

{#if data.items.length === 0}
  <section class="empty">
    {#if hasQuery}
      <h2>No matches for "{data.q}"</h2>
      <p>Try a different name or specialty.</p>
    {:else}
      <h2>No doctors found</h2>
      <p>Try a broader search, or browse all specialties.</p>
    {/if}
  </section>
{:else}
  <section class="grid">
    {#each data.items as doctor (doctor.slug)}
      <DoctorCard {doctor} />
    {/each}
  </section>
{/if}

<div class="pagination-wrap">
  <Pagination
    page={data.page}
    pageSize={data.pageSize}
    total={data.total}
    q={data.q ?? ""}
    specialty={data.selectedSlugs.join(",")}
    region={data.selectedRegion}
    city={data.selectedCity}
    sort={data.sort}
  />
</div>

<style>
  .search-strip {
    background: var(--bg-soft);
    border-bottom: 1px solid var(--line);
    padding: 1.5rem 0;
  }
  .search-strip-inner {
    max-width: 880px;
    margin: 0 auto;
    padding: 0 2rem;
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
  }
  .clear {
    color: var(--accent);
    font-size: 0.86rem;
    font-weight: 500;
    align-self: flex-end;
    transition: color 0.15s;
  }
  .clear:hover {
    color: var(--accent-deep);
    text-decoration: underline;
  }

  .section-head {
    max-width: 1280px;
    margin: 3rem auto 2rem;
    padding: 0 2rem;
    display: flex;
    justify-content: space-between;
    align-items: end;
    gap: 2rem;
  }
  .section-head h1 {
    font-family: var(--display);
    font-weight: 600;
    font-size: 2rem;
    letter-spacing: -0.02em;
    color: var(--ink);
    margin: 0 0 0.4rem;
  }
  .section-head p {
    color: var(--ink-muted);
    margin: 0;
    font-size: 0.95rem;
  }
  .section-head .meta {
    display: flex;
    align-items: center;
    gap: 1rem;
    color: var(--ink-faint);
    font-size: 0.86rem;
    font-weight: 500;
    white-space: nowrap;
  }

  .grid {
    max-width: 1280px;
    margin: 0 auto 2rem;
    padding: 0 2rem;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
  }

  .empty {
    max-width: 720px;
    margin: 6rem auto 4rem;
    padding: 3rem 2rem;
    text-align: center;
    background: var(--bg-soft);
    border: 1px solid var(--line);
    border-radius: 14px;
  }
  .empty h2 {
    font-family: var(--display);
    font-weight: 600;
    font-size: 1.5rem;
    color: var(--ink);
    margin: 0 0 0.5rem;
    letter-spacing: -0.02em;
  }
  .empty p {
    color: var(--ink-muted);
    margin: 0;
  }

  .pagination-wrap {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 2rem 2rem;
  }

  @media (max-width: 1000px) {
    .grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  @media (max-width: 600px) {
    .grid {
      grid-template-columns: 1fr;
      padding: 0 1.25rem;
    }
    .section-head {
      flex-direction: column;
      align-items: flex-start;
      padding: 0 1.25rem;
    }
    .search-strip-inner {
      padding: 0 1.25rem;
    }
  }
</style>
