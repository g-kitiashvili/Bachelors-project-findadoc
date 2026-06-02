<script lang="ts">
  import * as m from '$lib/paraglide/messages';
  import TriageWizard from '$lib/triage/TriageWizard.svelte';
  let { data } = $props();
</script>

<svelte:head><title>{m.triage_title()}</title></svelte:head>

<section class="page">
  <h1>{m.triage_heading()}</h1>
  <p class="intro">{m.triage_intro()}</p>
  <TriageWizard graph={data.graph} names={data.names} />
</section>

<style>
  .page { max-width: 720px; margin: 3rem auto; padding: 0 2rem; }
  h1 { font-family: var(--display); font-size: 2rem; letter-spacing: -0.02em; margin: 0 0 0.5rem; }
  .intro { color: var(--ink-muted); margin: 0 0 2rem; }
</style>
