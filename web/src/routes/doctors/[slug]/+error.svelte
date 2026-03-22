<script lang="ts">
  import { page } from "$app/state";
</script>

<svelte:head>
  <title>Not found — Find-a-Doc</title>
</svelte:head>

<section class="not-found">
  <div class="eyebrow">{page.status === 404 ? "404 · Not found" : `${page.status} · Error`}</div>
  <h1>
    {#if page.status === 404}
      We couldn't find that doctor.
    {:else}
      Something went wrong.
    {/if}
  </h1>
  <p class="detail">{page.error?.message ?? "The page you requested doesn't exist or is no longer available."}</p>
  <a class="back" href="/doctors">← Back to all doctors</a>
</section>

<style>
  .not-found {
    max-width: 640px;
    margin: 5rem auto 4rem;
    padding: 3rem 2rem;
    text-align: center;
    background: var(--bg-soft);
    border: 1px solid var(--line);
    border-radius: 16px;
  }
  .eyebrow {
    color: var(--accent);
    font-size: 0.82rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 1rem;
  }
  h1 {
    font-family: var(--display);
    font-weight: 600;
    font-size: 1.8rem;
    letter-spacing: -0.02em;
    color: var(--ink);
    margin: 0 0 1rem;
  }
  .detail {
    color: var(--ink-muted);
    margin: 0 0 2rem;
    line-height: 1.55;
  }
  .back {
    display: inline-block;
    background: var(--ink);
    color: white;
    padding: 0.7rem 1.4rem;
    border-radius: 8px;
    font-size: 0.92rem;
    font-weight: 500;
    transition: background 0.15s;
  }
  .back:hover {
    background: var(--accent);
  }
  @media (max-width: 600px) {
    .not-found {
      margin: 3rem 1.25rem;
      padding: 2.5rem 1.5rem;
    }
  }
</style>
