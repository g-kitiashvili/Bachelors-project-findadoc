<script lang="ts">
  let { data } = $props();
</script>

<svelte:head><title>Conditions — Find-a-Doc</title></svelte:head>

<section class="wrap">
  <h1>Conditions</h1>
  <p class="sub">Browse {data.conditions.length} conditions — each links to the specialists who treat it.</p>
  <ul class="list">
    {#each data.conditions as c (c.slug)}
      <li>
        <a href={`/conditions/${c.slug}`}>
          <span class="name">{c.nameEn}</span>
          <span class="count">{c.doctorCount} {c.doctorCount === 1 ? "doctor" : "doctors"}</span>
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
