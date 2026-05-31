<script lang="ts">
  import DoctorCard from "$lib/components/DoctorCard.svelte";
  import Pagination from "$lib/components/Pagination.svelte";
  import * as m from "$lib/paraglide/messages";
  import { href, localizedField } from "$lib/i18n";
  import { getLocale } from "$lib/paraglide/runtime";

  let { data } = $props();
</script>

<svelte:head><title>{`${localizedField(data.detail.nameKa, data.detail.nameEn, getLocale())}${m.meta_suffix()}`}</title></svelte:head>

<nav class="crumbs">
  <a href={href("/specialties")}>{m.specialties_heading()}</a>
  <span>·</span>
  <strong>{localizedField(data.detail.nameKa, data.detail.nameEn, getLocale())}</strong>
</nav>

<section class="hero">
  <h1>{localizedField(data.detail.nameKa, data.detail.nameEn, getLocale())}</h1>
  {#if localizedField(data.detail.descriptionKa, data.detail.descriptionEn, getLocale())}
    <p>{localizedField(data.detail.descriptionKa, data.detail.descriptionEn, getLocale())}</p>
  {/if}
  <div class="stats">
    <div class="stat"><b>{data.detail.doctorCount}</b><span>{data.detail.doctorCount === 1 ? m.noun_doctor() : m.noun_doctors()}</span></div>
    <div class="stat"><b>{data.detail.acceptingCount}</b><span>{m.stat_accepting_new()}</span></div>
    <div class="stat"><b>{data.detail.treatsChildrenCount}</b><span>{m.stat_treat_children()}</span></div>
  </div>
</section>

{#if data.list.items.length === 0}
  <section class="empty"><h2>{m.empty_no_doctors_yet()}</h2></section>
{:else}
  <section class="grid">
    {#each data.list.items as doctor (doctor.slug)}
      <DoctorCard {doctor} />
    {/each}
  </section>
  <div class="pagination-wrap">
    <Pagination page={data.list.page} pageSize={data.list.pageSize} total={data.list.total} />
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
  .hero h1 { font-family: var(--display); font-size: 2.5rem; letter-spacing: -0.02em; margin: 0 0 1.25rem; }
  .hero p { line-height: 1.55; max-width: 70ch; margin: 0 0 1.5rem; color: rgba(255,255,255,0.95); }
  .stats { display: flex; gap: 2rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2); flex-wrap: wrap; }
  .stat b { display: block; font-size: 1.5rem; font-weight: 600; }
  .stat span { font-size: 0.86rem; color: rgba(255,255,255,0.85); }

  .grid { max-width: 1280px; margin: 0 auto 2rem; padding: 0 2rem; display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
  .empty { max-width: 720px; margin: 4rem auto; padding: 3rem 2rem; text-align: center; background: var(--bg-soft); border-radius: 14px; }
  .pagination-wrap { max-width: 1280px; margin: 0 auto; padding: 0 2rem 2rem; }
</style>
