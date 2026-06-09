<script lang="ts">
  import * as m from "$lib/paraglide/messages";
  import { href, localizedField } from "$lib/i18n";
  import { getLocale } from "$lib/paraglide/runtime";

  let { data } = $props();

  let query = $state("");
  const filtered = $derived.by(() => {
    const q = query.trim().toLowerCase();
    if (!q) return data.conditions;
    return data.conditions.filter(
      (c) => c.nameKa.toLowerCase().includes(q) || c.nameEn.toLowerCase().includes(q),
    );
  });
</script>

<svelte:head><title>{m.meta_conditions()}</title></svelte:head>

<section class="wrap">
  <h1>{m.conditions_heading()}</h1>
  <p class="sub">{m.conditions_intro({ count: data.conditions.length })}</p>

  <input
    class="filter"
    type="search"
    bind:value={query}
    placeholder={m.conditions_search_placeholder()}
    aria-label={m.conditions_search_placeholder()} />

  {#if filtered.length === 0}
    <p class="empty">{m.search_no_matches()}</p>
  {:else}
    <ul class="list">
      {#each filtered as c (c.slug)}
        <li>
          <a href={href(`/conditions/${c.slug}`)}>
            <span class="name">{localizedField(c.nameKa, c.nameEn, getLocale())}</span>
            <span class="count">{c.doctorCount} {c.doctorCount === 1 ? m.noun_doctor() : m.noun_doctors()}</span>
          </a>
        </li>
      {/each}
    </ul>
  {/if}
</section>

<style>
  .wrap { max-width: 800px; margin: 3rem auto; padding: 0 2rem; }
  h1 { font-family: var(--display); font-size: 2.25rem; letter-spacing: -0.02em; margin: 0 0 0.5rem; }
  .sub { color: var(--ink-muted); margin: 0 0 1.5rem; }
  .filter {
    width: 100%;
    box-sizing: border-box;
    padding: 0.8rem 1rem;
    margin: 0 0 1.5rem;
    border: 1px solid var(--line-strong);
    border-radius: 10px;
    background: var(--surface);
    font-size: 1rem;
    color: var(--ink);
    transition: border-color 0.15s, box-shadow 0.15s;
  }
  .filter::placeholder { color: var(--ink-faint); }
  .filter:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 4px var(--accent-soft); }
  .empty { color: var(--ink-muted); padding: 1rem 0; }
  .list { list-style: none; padding: 0; margin: 0; border-top: 1px solid var(--line); }
  .list li a { display: flex; justify-content: space-between; align-items: center; padding: 1rem 0; border-bottom: 1px solid var(--line); color: var(--ink); transition: color 0.15s; text-decoration: none; }
  .list li a:hover { color: var(--accent); }
  .name { font-weight: 500; }
  .count { color: var(--ink-faint); font-size: 0.86rem; }
</style>
