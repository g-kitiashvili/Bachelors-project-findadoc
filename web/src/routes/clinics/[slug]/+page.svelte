<script lang="ts">
  import DoctorCard from "$lib/components/DoctorCard.svelte";
  import Pagination from "$lib/components/Pagination.svelte";

  let { data } = $props();
</script>

<svelte:head><title>{data.detail.nameEn} — Find-a-Doc</title></svelte:head>

<nav class="crumbs">
  <a href="/clinics">Clinics</a>
  <span>·</span>
  <strong>{data.detail.nameEn}</strong>
</nav>

<section class="hero">
  <h1>{data.detail.nameEn}</h1>
  <div class="ka">{data.detail.nameKa}</div>
  <div class="details">
    {#if data.detail.address}
      <span class="detail">{data.detail.address}</span>
    {/if}
    {#if data.detail.phone}
      <span class="detail">{data.detail.phone}</span>
    {/if}
    {#if data.detail.website}
      <a class="detail link" href={data.detail.website} target="_blank" rel="noopener noreferrer">{data.detail.website}</a>
    {/if}
  </div>
  <div class="stats">
    <div class="stat"><b>{data.detail.doctorCount}</b><span>{data.detail.doctorCount === 1 ? "doctor" : "doctors"}</span></div>
  </div>
</section>

{#if data.list.items.length === 0}
  <section class="empty"><h2>No doctors yet</h2></section>
{:else}
  <section class="grid">
    {#each data.list.items as doctor (doctor.slug)}
      <DoctorCard {doctor} />
    {/each}
  </section>
  <div class="pagination-wrap">
    <Pagination page={data.list.page} pageSize={data.list.pageSize} total={data.list.total} q={""} />
  </div>
{/if}

<style>
  .crumbs { max-width: 1280px; margin: 2rem auto 1rem; padding: 0 2rem; color: var(--ink-faint); font-size: 0.86rem; }
  .crumbs a { color: var(--ink-muted); text-decoration: none; }
  .crumbs a:hover { text-decoration: underline; }
  .crumbs strong { color: var(--ink); font-weight: 600; margin-left: 0.4rem; }
  .crumbs span { margin: 0 0.4rem; }

  .hero {
    max-width: 1280px;
    margin: 0 2rem 2.5rem;
    padding: 2.5rem 2.5rem;
    background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
    color: white;
    border-radius: 14px;
  }
  @media (min-width: 1320px) {
    .hero { margin: 0 auto 2.5rem; }
  }
  .hero h1 { font-family: var(--display); font-size: 2.5rem; letter-spacing: -0.02em; margin: 0 0 0.4rem; }
  .hero .ka { color: rgba(255,255,255,0.8); font-style: italic; margin-bottom: 1.25rem; }
  .details { display: flex; flex-wrap: wrap; gap: 1.25rem; margin-bottom: 1.5rem; }
  .detail { color: rgba(255,255,255,0.95); font-size: 0.95rem; }
  .detail.link { color: white; text-decoration: underline; }
  .stats { display: flex; gap: 2rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2); flex-wrap: wrap; }
  .stat b { display: block; font-size: 1.5rem; font-weight: 600; }
  .stat span { font-size: 0.86rem; color: rgba(255,255,255,0.85); }

  .grid { max-width: 1280px; margin: 0 auto 2rem; padding: 0 2rem; display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
  .empty { max-width: 720px; margin: 4rem auto; padding: 3rem 2rem; text-align: center; background: var(--bg-soft); border-radius: 14px; }
  .pagination-wrap { max-width: 1280px; margin: 0 auto; padding: 0 2rem 2rem; }
</style>
