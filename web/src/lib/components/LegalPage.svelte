<script lang="ts">
  import type { Snippet } from "svelte";

  let { title, children }: { title: string; children: Snippet } = $props();
</script>

<svelte:head><title>{title}</title></svelte:head>

<article class="legal">
  {@render children()}
</article>

<style>
  .legal {
    max-width: 760px;
    margin: 3rem auto 4rem;
    padding: 0 2rem;
    color: var(--ink);
    line-height: 1.65;
  }
  .legal :global(h1) {
    font-family: var(--display);
    font-size: 2.1rem;
    letter-spacing: -0.02em;
    margin: 0 0 0.5rem;
  }
  .legal :global(.updated) {
    color: var(--ink-faint);
    font-size: 0.86rem;
    margin: 0 0 2rem;
  }
  .legal :global(h2) {
    font-size: 1.2rem;
    font-weight: 600;
    margin: 2rem 0 0.6rem;
  }
  .legal :global(p) {
    color: var(--ink-muted);
    margin: 0 0 1rem;
  }
  .legal :global(ul) {
    color: var(--ink-muted);
    margin: 0 0 1rem;
    padding-left: 1.25rem;
  }
  .legal :global(li) {
    margin: 0 0 0.4rem;
  }
  .legal :global(a) {
    color: var(--accent);
    text-decoration: underline;
  }
</style>
