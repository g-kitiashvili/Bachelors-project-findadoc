<script lang="ts">
  let { data } = $props();
</script>

<svelte:head><title>Specialties — Find-a-Doc</title></svelte:head>

<section class="wrap">
  <h1>Specialties</h1>
  <p class="sub">Browse {data.specialties.length} medical specialties — filter the doctor list or read about each field.</p>

  <ul class="list">
    {#each data.specialties as s (s.slug)}
      <li>
        <a href={`/specialties/${s.slug}`}>
          <span class="name">{s.nameEn}</span>
          <span class="count">{s.doctorCount} {s.doctorCount === 1 ? "doctor" : "doctors"}</span>
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
