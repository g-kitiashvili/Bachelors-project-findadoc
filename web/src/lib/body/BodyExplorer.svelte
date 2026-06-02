<script lang="ts">
  import * as m from '$lib/paraglide/messages';
  import { href } from '$lib/i18n';
  import { onMount } from 'svelte';
  import { hasWebGL } from '$lib/body/webgl';
  import BodyScene from '$lib/body/BodyScene.svelte';
  import BodyPanel from '$lib/body/BodyPanel.svelte';
  import { bodyMap, type TargetId } from '$lib/body/regions';
  import { getLocale } from '$lib/paraglide/runtime';
  import type { TriageGraph } from '$lib/triage';

  let { graph, names }: { graph: TriageGraph; names: Record<string, { ka: string; en: string }> } = $props();
  let webgl = $state(true);
  let picked = $state<TargetId | null>(null);
  let hovered = $state<TargetId | null>(null);
  const loc = (t: { ka: string; en: string }) => (getLocale() === 'ka' ? t.ka : t.en);
  const sideList: TargetId[] = ['skin', 'allergies', 'womens-health', 'mens-health', 'breast', 'child', 'mental', 'not-sure'];

  onMount(() => { webgl = hasWebGL(); });
</script>

{#if !webgl}
  <div class="fallback">
    <p>{m.body_nowebgl()}</p>
    <a class="cta" href={href('/triage')}>{m.body_nowebgl_cta()}</a>
  </div>
{:else}
  <div class="layout">
    <div class="stage">
      <BodyScene onpick={(id) => (picked = id)} onhover={(id) => (hovered = id)} />
      {#if hovered}<span class="hover-tag">{loc(bodyMap[hovered][0].label)}</span>{/if}
    </div>
    <aside class="side">
      <BodyPanel targetId={picked} {graph} {names} />
      <div class="other">
        <p class="other-lbl">{m.body_other()}</p>
        {#each sideList as id (id)}
          <button type="button" class="chip" onclick={() => (picked = id)}>{loc(bodyMap[id][0].label)}</button>
        {/each}
      </div>
    </aside>
  </div>
{/if}

<style>
  .layout { display: grid; grid-template-columns: 1.4fr 1fr; gap: 2rem; align-items: start; }
  .stage { position: relative; height: 560px; }
  .hover-tag { position: absolute; top: 12px; right: 12px; background: rgba(0,0,0,0.7); color: #fff; padding: 0.3rem 0.6rem; border-radius: 8px; font-size: 0.85rem; }
  .side { padding-top: 0.5rem; }
  .other { margin-top: 1.5rem; border-top: 1px solid var(--line); padding-top: 1rem; }
  .other-lbl { font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink-faint); font-weight: 700; margin: 0 0 0.6rem; }
  .chip { font-size: 0.85rem; padding: 0.4rem 0.8rem; margin: 0 0.4rem 0.4rem 0; border-radius: 100px; border: 1px dashed var(--line-strong); background: transparent; color: var(--ink-muted); cursor: pointer; }
  .chip:hover { border-color: var(--accent); color: var(--accent); }
  .fallback { background: var(--bg-soft); border: 1px solid var(--line); border-radius: 14px; padding: 2rem; text-align: center; }
  .fallback .cta { display: inline-block; margin-top: 1rem; background: var(--accent); color: #fff; padding: 0.7rem 1.2rem; border-radius: 10px; text-decoration: none; font-weight: 600; }
  @media (max-width: 860px) { .layout { grid-template-columns: 1fr; } }
</style>
