<script lang="ts">
  import * as m from '$lib/paraglide/messages';
  import { href } from '$lib/i18n';
  import { getLocale } from '$lib/paraglide/runtime';
  import { advance, toggleSymptom, submit, type TriageGraph, type TriageOption, type TriageState, type ScoredResult } from '$lib/triage';
  import { bodyMap, type TargetId } from './regions';

  let { targetId, graph, names }:
    { targetId: TargetId | null; graph: TriageGraph; names: Record<string, { ka: string; en: string }> } = $props();

  const loc = (t: { ka: string; en: string }) => (getLocale() === 'ka' ? t.ka : t.en);
  const nameOf = (r: ScoredResult) => { const n = names[`${r.type}:${r.slug}`]; return n ? loc(n) : r.slug; };

  let flow = $state<TriageState | null>(null);
  let lastTarget = $state<TargetId | null>(null);

  $effect(() => {
    if (targetId !== lastTarget) { lastTarget = targetId; flow = null; }
  });

  const options = $derived(targetId ? bodyMap[targetId] : []);
  const node = $derived(flow && !flow.ranked ? graph.nodes[flow.currentId] : null);

  function choose(opt: TriageOption) {
    flow = advance(graph, { currentId: graph.start, history: [], selected: [], ranked: null }, opt);
  }
  function toggle(i: number) { if (flow) flow = toggleSymptom(flow, i); }
  function seeMatches() { if (flow) flow = submit(graph, flow); }
  function resultHref(r: ScoredResult) { return href(r.type === 'specialty' ? `/specialties/${r.slug}` : `/conditions/${r.slug}`); }
  function reset() { flow = null; }
</script>

<div class="panel">
  {#if !targetId}
    <p class="hint">{m.body_hint()}</p>
  {:else if flow?.ranked}
    {@const top = flow.ranked[0]}
    <p class="eyebrow">{m.triage_results_eyebrow()}</p>
    <h3 class="lead">{m.triage_results_lead({ name: nameOf(top) })}</h3>
    <p class="disclaimer">{m.triage_disclaimer()}</p>
    {#each flow.ranked as r, i (r.type + r.slug)}
      <a class="match" class:top={i === 0} href={resultHref(r)}>
        <span class="rank">{i + 1}</span>
        <span class="mname">{nameOf(r)}{#if i === 0}<span class="badge">{m.triage_best_match()}</span>{/if}</span>
        <span class="go">{m.triage_see_doctors()}</span>
      </a>
    {/each}
    <button class="link" type="button" onclick={reset}>{m.triage_start_over()}</button>
  {:else if flow && node?.symptoms}
    <h3 class="q">{loc(node.question)}</h3>
    <p class="hint">{m.triage_symptom_hint()}</p>
    {#each node.symptoms as sym, i (i)}
      <button type="button" class="sym" class:sel={flow.selected.includes(i)} onclick={() => toggle(i)}>{loc(sym.label)}</button>
    {/each}
    <button class="cta" type="button" disabled={flow.selected.length === 0} onclick={seeMatches}>{m.triage_symptom_cta()}</button>
    <button class="link" type="button" onclick={reset}>{m.triage_back()}</button>
  {:else}
    <h3 class="q">{m.body_refine()}</h3>
    {#each options as opt (loc(opt.label))}
      <button type="button" class="opt" onclick={() => choose(opt)}>{loc(opt.label)}</button>
    {/each}
  {/if}
</div>

<style>
  .panel { display: flex; flex-direction: column; gap: 0.55rem; }
  .hint { color: var(--ink-muted); font-size: 0.9rem; }
  .q { font-family: var(--display); font-size: 1.2rem; margin: 0 0 0.25rem; }
  .opt, .sym { text-align: left; padding: 0.8rem 1rem; border: 1px solid var(--line); border-radius: 10px; background: var(--surface); color: var(--ink); cursor: pointer; }
  .opt:hover, .sym:hover { border-color: var(--accent); background: var(--accent-soft); }
  .sym.sel { border-color: var(--accent); background: var(--accent-soft); }
  .cta { background: var(--accent); color: #fff; border: none; padding: 0.75rem 1.1rem; border-radius: 10px; font-weight: 600; cursor: pointer; }
  .cta:disabled { opacity: 0.5; cursor: not-allowed; }
  .link { background: none; border: none; color: var(--ink-muted); cursor: pointer; font-size: 0.88rem; text-align: left; padding: 0; }
  .eyebrow { font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--accent); font-weight: 700; margin: 0; }
  .lead { font-family: var(--display); font-size: 1.3rem; margin: 0.2rem 0; }
  .disclaimer { color: var(--ink-faint); font-size: 0.82rem; margin: 0 0 0.6rem; }
  .match { display: flex; align-items: center; gap: 0.7rem; background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 0.8rem 0.9rem; text-decoration: none; color: var(--ink); }
  .match.top { border-color: var(--accent); background: var(--accent-soft); }
  .rank { width: 24px; height: 24px; border-radius: 50%; background: var(--bg-soft); color: var(--accent-deep); font-weight: 700; font-size: 0.78rem; display: flex; align-items: center; justify-content: center; flex: none; }
  .mname { flex: 1; font-weight: 600; }
  .badge { font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; color: var(--accent-deep); background: var(--bg-soft); padding: 0.15rem 0.4rem; border-radius: 6px; margin-left: 0.4rem; }
  .go { color: var(--accent); font-weight: 600; font-size: 0.85rem; white-space: nowrap; }
</style>
