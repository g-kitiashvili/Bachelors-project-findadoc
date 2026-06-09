<script lang="ts">
  import * as m from "$lib/paraglide/messages";
  import { href, localizedField } from "$lib/i18n";
  import { getLocale } from "$lib/paraglide/runtime";

  let { data } = $props();
  let open = $state<Record<string, boolean>>({});

  let query = $state("");
  const filtered = $derived.by(() => {
    const q = query.trim().toLowerCase();
    if (!q) return data.items;
    const hit = (ka: string, en: string) => ka.toLowerCase().includes(q) || en.toLowerCase().includes(q);
    return data.items.filter(
      (c) => hit(c.nameKa, c.nameEn) || (c.branches ?? []).some((b) => hit(b.nameKa, b.nameEn)),
    );
  });
</script>

<svelte:head><title>{m.meta_clinics()}</title></svelte:head>

<section class="wrap">
  <h1>{m.clinics_heading()}</h1>
  <p class="sub">{`${data.total} ${data.total === 1 ? m.noun_clinic() : m.noun_clinics()} ${m.clinics_subtitle_suffix()}`}</p>

  <input
    class="filter"
    type="search"
    bind:value={query}
    placeholder={m.clinics_search_placeholder()}
    aria-label={m.clinics_search_placeholder()} />

  {#if filtered.length === 0}
    <p class="empty">{data.items.length === 0 ? m.clinics_none() : m.search_no_matches()}</p>
  {:else}
    <ul class="list">
      {#each filtered as c (c.slug)}
        <li>
          {#if c.branches && c.branches.length > 0}
            <button type="button" class="row brandrow" aria-expanded={open[c.slug] ?? false} onclick={() => (open[c.slug] = !open[c.slug])}>
              <span class="name">{localizedField(c.nameKa, c.nameEn, getLocale())} <span class="brandtag">{c.branches.length} {m.noun_branches()}</span></span>
              <span class="count">{c.doctorCount} {c.doctorCount === 1 ? m.noun_doctor() : m.noun_doctors()} <span class="chev">{(open[c.slug] ?? false) ? "▾" : "▸"}</span></span>
            </button>
            {#if open[c.slug]}
              <ul class="branches">
                {#each c.branches as b (b.slug)}
                  <li><a href={href(`/clinics/${b.slug}`)}><span class="bname">{localizedField(b.nameKa, b.nameEn, getLocale())}</span>{#if b.address}<span class="baddr">{b.address}</span>{/if}</a></li>
                {/each}
              </ul>
            {/if}
          {:else}
            <a class="row" href={href(`/clinics/${c.slug}`)}>
              <span class="name">{localizedField(c.nameKa, c.nameEn, getLocale())}</span>
              <span class="count">{c.doctorCount} {c.doctorCount === 1 ? m.noun_doctor() : m.noun_doctors()}</span>
            </a>
          {/if}
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

  .list { list-style: none; padding: 0; margin: 0; border-top: 1px solid var(--line); }
  .row { display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 1rem 0; border: 0; border-bottom: 1px solid var(--line); color: var(--ink); transition: color 0.15s; text-decoration: none; background: none; font: inherit; text-align: left; cursor: pointer; }
  .row:hover { color: var(--accent); }
  .brandtag { color: var(--ink-faint); font-size: 0.78rem; font-weight: 400; margin-left: 0.5rem; }
  .chev { color: var(--ink-faint); margin-left: 0.4rem; }
  .branches { list-style: none; margin: 0 0 0.5rem; padding: 0 0 0 1.25rem; }
  .branches li a { display: flex; justify-content: space-between; align-items: baseline; gap: 1rem; padding: 0.55rem 0; border-bottom: 1px solid var(--line); color: var(--ink-muted); text-decoration: none; }
  .branches li a:hover { color: var(--accent); }
  .branches .baddr { color: var(--ink-faint); font-size: 0.82rem; }
  .name { font-weight: 500; }
  .count { color: var(--ink-faint); font-size: 0.86rem; }

  .empty { padding: 1rem 0; color: var(--ink-muted); }
</style>
