<script lang="ts">
  import * as m from "$lib/paraglide/messages";
  import { href, localizedField } from "$lib/i18n";
  import { getLocale } from "$lib/paraglide/runtime";

  let { data } = $props();
</script>

<svelte:head><title>{m.meta_conditions()}</title></svelte:head>

<section class="wrap">
  <h1>{m.conditions_heading()}</h1>
  <p class="sub">{m.conditions_intro({ count: data.conditions.length })}</p>
  <ul class="list">
    {#each data.conditions as c (c.slug)}
      <li>
        <a href={href(`/conditions/${c.slug}`)}>
          <span class="name">{localizedField(c.nameKa, c.nameEn, getLocale())}</span>
          <span class="count">{c.doctorCount} {c.doctorCount === 1 ? m.noun_doctor() : m.noun_doctors()}</span>
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
