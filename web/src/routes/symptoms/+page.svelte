<script lang="ts">
  import * as m from '$lib/paraglide/messages';
  import TriageWizard from '$lib/triage/TriageWizard.svelte';
  import BodyExplorer from '$lib/body/BodyExplorer.svelte';

  let { data } = $props();
  let tab = $state<'questions' | 'body'>('questions');
</script>

<svelte:head><title>{m.symptoms_heading()}</title></svelte:head>

<section class="symptoms">
  <h1>{m.symptoms_heading()}</h1>
  <p class="intro">{m.symptoms_intro()}</p>

  <div class="tabs" role="tablist">
    <button class="tab" class:active={tab === 'questions'} role="tab" aria-selected={tab === 'questions'} onclick={() => (tab = 'questions')}>{m.tab_questions()}</button>
    <button class="tab" class:active={tab === 'body'} role="tab" aria-selected={tab === 'body'} onclick={() => (tab = 'body')}>{m.tab_body()}</button>
  </div>

  {#if tab === 'questions'}
    <TriageWizard graph={data.graph} names={data.names} />
  {:else}
    <BodyExplorer graph={data.graph} names={data.names} />
  {/if}
</section>

<style>
  .symptoms { max-width: 1100px; margin: 2.5rem auto; padding: 0 2rem; }
  h1 { font-family: var(--display); font-size: 2rem; margin: 0 0 0.4rem; }
  .intro { color: var(--ink-muted); margin: 0 0 1.25rem; }
  .tabs { display: flex; gap: 0.5rem; border-bottom: 1px solid var(--line); margin-bottom: 1.5rem; }
  .tab { background: none; border: none; border-bottom: 2px solid transparent; padding: 0.6rem 0.9rem; font-size: 0.95rem; font-weight: 600; color: var(--ink-muted); cursor: pointer; margin-bottom: -1px; }
  .tab:hover { color: var(--ink); }
  .tab.active { color: var(--accent); border-bottom-color: var(--accent); }
</style>
