<script lang="ts">
  let { data } = $props();
</script>

<main>
  <h1>Find-a-Doc</h1>
  {#if data.doctor}
    <p>
      Walking skeleton OK. Loaded doctor:
      <strong>{data.doctor.fullName}</strong>
      (slug: <code>{data.doctor.slug}</code>) from the API.
    </p>
  {:else}
    <p>
      Could not reach the API at <code>{data.apiBase}</code>. Make sure the
      backend is running.
    </p>
  {/if}
</main>

<style>
  main {
    padding: 2rem;
    font-family: system-ui, sans-serif;
  }
</style>
