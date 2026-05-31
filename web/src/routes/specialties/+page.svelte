<script lang="ts">
  import * as m from "$lib/paraglide/messages";
  import { href, localizedField } from "$lib/i18n";
  import { getLocale } from "$lib/paraglide/runtime";

  let { data } = $props();
</script>

<svelte:head><title>{m.meta_specialties()}</title></svelte:head>

<section class="wrap">
  <h1>{m.specialties_heading()}</h1>
  <p class="sub">{m.specialties_intro({ count: data.specialties.length })}</p>

  <ul class="list">
    {#each data.specialties as s (s.slug)}
      <li>
        <a href={href(`/specialties/${s.slug}`)}>
          <span class="name">{localizedField(s.nameKa, s.nameEn, getLocale())}</span>
          <span class="count">{s.doctorCount} {s.doctorCount === 1 ? m.noun_doctor() : m.noun_doctors()}</span>
        </a>
      </li>
    {/each}
  </ul>
</section>

<style>
  .wrap { max-width: 800px; margin: 3rem auto; padding: 0 2rem; }
  h1 { font-family: var(--display); font-size: 2.25rem; letter-spacing: -0.02em; margin: 0 0 0.5rem; }
  .sub { color: var(--ink-muted); margin: 0 0 2rem; }
  .list { list-style: none; padding: 0; margin: 0; border-top: 1px solid var(--line); }
  .list li a { display: flex; justify-content: space-between; align-items: center; padding: 1rem 0; border-bottom: 1px solid var(--line); color: var(--ink); transition: color 0.15s; text-decoration: none; }
  .list li a:hover { color: var(--accent); }
  .name { font-weight: 500; }
  .count { color: var(--ink-faint); font-size: 0.86rem; }
</style>
