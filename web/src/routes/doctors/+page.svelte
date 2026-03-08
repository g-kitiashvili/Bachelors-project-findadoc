<script lang="ts">
  import DoctorCard from "$lib/components/DoctorCard.svelte";
  import Pagination from "$lib/components/Pagination.svelte";

  let { data } = $props();
</script>

<main>
  <h1>Doctors</h1>

  {#if data.items.length === 0}
    <p class="empty">No doctors found.</p>
  {:else}
    <ul class="grid">
      {#each data.items as doctor (doctor.slug)}
        <li><DoctorCard {doctor} /></li>
      {/each}
    </ul>
  {/if}

  <Pagination page={data.page} pageSize={data.pageSize} total={data.total} />
</main>

<style>
  main {
    max-width: 720px;
    margin: 2rem auto;
    padding: 0 1rem;
    font-family: system-ui, sans-serif;
  }
  h1 {
    margin-bottom: 1.5rem;
  }
  .empty {
    color: #777;
    text-align: center;
    margin: 3rem 0;
  }
  .grid {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }
</style>
