<script lang="ts">
  import Pagination from "$lib/components/Pagination.svelte";

  let { data } = $props();
  let open = $state<Record<string, boolean>>({});
</script>

<svelte:head>
  <title>{data.q ? `Search · ${data.q}` : "Clinics"} — Find-a-Doc</title>
</svelte:head>

<section class="wrap">
  <h1>Clinics</h1>
  <p class="sub">{data.total} {data.total === 1 ? "clinic" : "clinics"} with active doctors</p>

  <form method="get" action="/clinics" class="search-form">
    <input
      type="search"
      name="q"
      value={data.q}
      placeholder="Search by clinic name…"
      class="search-input"
    />
    <button type="submit" class="search-btn">Search</button>
    {#if data.q}
      <a href="/clinics" class="clear-link">Clear</a>
    {/if}
  </form>

  {#if data.items.length === 0}
    <div class="empty">
      {#if data.q}
        <p>No clinics matched <strong>"{data.q}"</strong>. Try a different name.</p>
      {:else}
        <p>No clinics found.</p>
      {/if}
    </div>
  {:else}
    <ul class="list">
      {#each data.items as c (c.slug)}
        <li>
          {#if c.branches && c.branches.length > 0}
            <button type="button" class="row brandrow" aria-expanded={open[c.slug] ?? false} onclick={() => (open[c.slug] = !open[c.slug])}>
              <span class="name">{c.nameEn} <span class="brandtag">{c.branches.length} branches</span></span>
              <span class="count">{c.doctorCount} {c.doctorCount === 1 ? "doctor" : "doctors"} <span class="chev">{(open[c.slug] ?? false) ? "▾" : "▸"}</span></span>
            </button>
            {#if open[c.slug]}
              <ul class="branches">
                {#each c.branches as b (b.slug)}
                  <li><a href={`/clinics/${b.slug}`}><span class="bname">{b.nameEn}</span>{#if b.address}<span class="baddr">{b.address}</span>{/if}</a></li>
                {/each}
              </ul>
            {/if}
          {:else}
            <a class="row" href={`/clinics/${c.slug}`}>
              <span class="name">{c.nameEn}</span>
              <span class="count">{c.doctorCount} {c.doctorCount === 1 ? "doctor" : "doctors"}</span>
            </a>
          {/if}
        </li>
      {/each}
    </ul>
  {/if}

  <Pagination page={data.page} pageSize={data.pageSize} total={data.total} />
</section>

<style>
  .wrap { max-width: 800px; margin: 3rem auto; padding: 0 2rem; }
  h1 { font-family: var(--display); font-size: 2.25rem; letter-spacing: -0.02em; margin: 0 0 0.5rem; }
  .sub { color: var(--ink-muted); margin: 0 0 1.75rem; }

  .search-form { display: flex; gap: 0.5rem; align-items: center; margin-bottom: 2rem; }
  .search-input {
    flex: 1;
    padding: 0.6rem 0.9rem;
    border: 1px solid var(--line);
    border-radius: 8px;
    font-size: 0.95rem;
    background: var(--surface);
    color: var(--ink);
    transition: border-color 0.15s;
  }
  .search-input:focus { outline: none; border-color: var(--accent); }
  .search-btn {
    padding: 0.6rem 1.1rem;
    background: var(--ink);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 0.92rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.15s;
  }
  .search-btn:hover { background: var(--accent); }
  .clear-link { font-size: 0.88rem; color: var(--ink-muted); white-space: nowrap; }
  .clear-link:hover { color: var(--ink); }

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

  .empty { padding: 3rem 0; color: var(--ink-muted); }
</style>
