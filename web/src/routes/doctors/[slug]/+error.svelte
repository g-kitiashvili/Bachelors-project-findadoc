<script lang="ts">
  import { page } from "$app/stores";
</script>

<main>
  <h1>
    {#if $page.status === 404}
      Doctor not found.
    {:else}
      Something went wrong.
    {/if}
  </h1>
  <p class="detail">{$page.error?.message ?? ""}</p>
  <a class="back" href="/doctors">← Back to doctors</a>
</main>

<style>
  main {
    max-width: 560px;
    margin: 4rem auto;
    padding: 0 1rem;
    text-align: center;
    font-family: system-ui, sans-serif;
  }
  .detail { color: #777; }
  .back {
    display: inline-block;
    margin-top: 1.5rem;
    color: #2563eb;
    text-decoration: none;
  }
</style>
