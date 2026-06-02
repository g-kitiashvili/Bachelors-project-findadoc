<script lang="ts">
  import * as m from '$lib/paraglide/messages';
  import BodyExplorer from '$lib/body/BodyExplorer.svelte';
  let { data } = $props();
</script>

<svelte:head><title>{m.body_title()}</title></svelte:head>

<section class="page">
  <h1>{m.body_heading()}</h1>
  <p class="intro">{m.body_intro()}</p>
  <BodyExplorer graph={data.graph} names={data.names} />
</section>

<style>
  .page { max-width: 1100px; margin: 2.5rem auto; padding: 0 2rem; }
  h1 { font-family: var(--display); font-size: 2rem; margin: 0 0 0.4rem; }
  .intro { color: var(--ink-muted); margin: 0 0 1.5rem; }
</style>
