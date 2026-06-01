<script lang="ts">
  import * as m from '$lib/paraglide/messages';
  import { href } from '$lib/i18n';
  import { getLocale } from '$lib/paraglide/runtime';
  import {
    initState, advance, back, toggleSymptom, submit,
    type TriageOption, type ScoredResult,
  } from '$lib/triage';

  let { data } = $props();
  const graph = data.graph;
  const names: Record<string, { ka: string; en: string }> = data.names ?? {};

  let state = $state(initState(graph));
  const node = $derived(graph.nodes[state.currentId]);
  const loc = (t: { ka: string; en: string }) => (getLocale() === 'ka' ? t.ka : t.en);
  const nameOf = (r: ScoredResult) => {
    const n = names[`${r.type}:${r.slug}`];
    return n ? loc(n) : r.slug;
  };

  function pickOption(opt: TriageOption) { state = advance(graph, state, opt); }
  function toggle(i: number) { state = toggleSymptom(state, i); }
  function seeMatches() { state = submit(graph, state); }
  function goBack() { state = back(state); }
  function reset() { state = initState(graph); }

  function resultHref(r: ScoredResult): string {
    return href(r.type === 'specialty' ? `/specialties/${r.slug}` : `/conditions/${r.slug}`);
  }

  const echo = $derived(
    state.currentId && graph.nodes[state.currentId]?.symptoms
      ? state.selected.map((i) => loc(graph.nodes[state.currentId].symptoms![i].label)).join(' · ')
      : '',
  );
</script>

<svelte:head><title>{m.triage_title()}</title></svelte:head>

<section class="triage">
  <h1>{m.triage_heading()}</h1>
  <p class="intro">{m.triage_intro()}</p>

  {#if state.ranked}
    {@const top = state.ranked[0]}
    {@const others = state.ranked.slice(1)}
    <div class="results">
      <p class="eyebrow">{m.triage_results_eyebrow()}</p>
      <h2 class="lead">{m.triage_results_lead({ name: nameOf(top) })}</h2>
      {#if echo}<p class="echo">{m.triage_symptom_echo()} {echo}</p>{/if}
      <p class="disclaimer">{m.triage_disclaimer()}</p>

      <a class="match top" href={resultHref(top)}>
        <span class="rank">1</span>
        <span class="match-name">{nameOf(top)} <span class="badge">{m.triage_best_match()}</span></span>
        <span class="go">{m.triage_see_doctors()}</span>
      </a>

      {#if others.length > 0}
        <p class="others-label">{m.triage_other_possibilities()}</p>
        {#each others as r, i (r.type + r.slug)}
          <a class="match" href={resultHref(r)}>
            <span class="rank">{i + 2}</span>
            <span class="match-name">{nameOf(r)}</span>
            <span class="go">{m.triage_see_doctors()}</span>
          </a>
        {/each}
      {/if}
    </div>
    <button type="button" class="link" onclick={reset}>{m.triage_start_over()}</button>
  {:else if node?.symptoms}
    <h2 class="question">{loc(node.question)}</h2>
    <p class="hint">{m.triage_symptom_hint()}</p>
    <div class="symptoms">
      {#each node.symptoms as sym, i (i)}
        <button type="button" class="symptom" class:sel={state.selected.includes(i)} onclick={() => toggle(i)}>
          <span class="box" aria-hidden="true"></span>
          {loc(sym.label)}
        </button>
      {/each}
    </div>
    <div class="controls">
      <button type="button" class="cta" disabled={state.selected.length === 0} onclick={seeMatches}>{m.triage_symptom_cta()}</button>
      {#if state.history.length > 0}<button type="button" class="link" onclick={goBack}>{m.triage_back()}</button>{/if}
      <button type="button" class="link" onclick={reset}>{m.triage_start_over()}</button>
    </div>
  {:else if node}
    <h2 class="question">{loc(node.question)}</h2>
    <div class="options">
      {#each node.options ?? [] as opt (loc(opt.label))}
        <button type="button" class="option" onclick={() => pickOption(opt)}>{loc(opt.label)}</button>
      {/each}
    </div>
    <div class="controls">
      {#if state.history.length > 0}<button type="button" class="link" onclick={goBack}>{m.triage_back()}</button>{/if}
      <button type="button" class="link" onclick={reset}>{m.triage_start_over()}</button>
    </div>
  {/if}
</section>

<style>
  .triage { max-width: 720px; margin: 3rem auto; padding: 0 2rem; }
  h1 { font-family: var(--display); font-size: 2rem; letter-spacing: -0.02em; margin: 0 0 0.5rem; }
  .intro { color: var(--ink-muted); margin: 0 0 2rem; }
  .question { font-family: var(--display); font-size: 1.45rem; font-weight: 600; margin: 0 0 0.35rem; }
  .hint { color: var(--ink-muted); font-size: 0.92rem; margin: 0 0 1.25rem; }

  .options, .symptoms { display: flex; flex-direction: column; gap: 0.6rem; }
  .option, .symptom {
    text-align: left; padding: 0.9rem 1.1rem; border: 1px solid var(--line);
    border-radius: 11px; background: var(--surface); color: var(--ink);
    font-size: 0.98rem; cursor: pointer; transition: border-color 0.15s, background 0.15s;
  }
  .option:hover, .symptom:hover { border-color: var(--accent); background: var(--accent-soft); }
  .symptom { display: flex; align-items: center; gap: 0.75rem; }
  .symptom .box { width: 18px; height: 18px; border-radius: 5px; border: 1.5px solid var(--line-strong); flex: none; }
  .symptom.sel { border-color: var(--accent); background: var(--accent-soft); }
  .symptom.sel .box { background: var(--accent); border-color: var(--accent); position: relative; }
  .symptom.sel .box::after { content: '✓'; color: white; font-size: 12px; position: absolute; top: -2px; left: 3px; }

  .controls { display: flex; align-items: center; gap: 1.25rem; margin-top: 1.75rem; }
  .cta {
    background: var(--accent); color: white; border: none; padding: 0.8rem 1.3rem;
    border-radius: 10px; font-weight: 600; font-size: 0.95rem; cursor: pointer;
  }
  .cta:hover { background: var(--accent-deep); }
  .cta:disabled { opacity: 0.5; cursor: not-allowed; }
  .link { background: none; border: none; color: var(--ink-muted); cursor: pointer; font-size: 0.9rem; padding: 0; }
  .link:hover { color: var(--accent); }

  .results { background: var(--bg-soft); border: 1px solid var(--line); border-radius: 14px; padding: 2rem; margin-bottom: 1.25rem; }
  .eyebrow { font-size: 0.74rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--accent); font-weight: 700; margin: 0 0 0.5rem; }
  .lead { font-family: var(--display); font-size: 1.5rem; font-weight: 600; margin: 0 0 0.5rem; }
  .echo { color: var(--ink-muted); font-size: 0.9rem; margin: 0 0 0.35rem; }
  .disclaimer { color: var(--ink-faint); font-size: 0.85rem; margin: 0 0 1.5rem; }
  .match {
    display: flex; align-items: center; gap: 0.9rem; background: white; border: 1px solid var(--line);
    border-radius: 12px; padding: 0.9rem 1rem; margin-bottom: 0.6rem; text-decoration: none; color: var(--ink);
  }
  .match.top { border-color: var(--accent); background: var(--accent-soft); padding: 1.1rem 1rem; }
  .match .rank { width: 26px; height: 26px; border-radius: 50%; background: var(--bg-soft); color: var(--accent-deep); font-weight: 700; font-size: 0.8rem; display: flex; align-items: center; justify-content: center; flex: none; }
  .match.top .rank { background: var(--accent); color: white; }
  .match-name { flex: 1; font-weight: 600; }
  .badge { display: inline-block; font-size: 0.62rem; letter-spacing: 0.06em; text-transform: uppercase; font-weight: 700; color: var(--accent-deep); background: var(--bg-soft); padding: 0.18rem 0.45rem; border-radius: 6px; margin-left: 0.4rem; }
  .go { color: var(--accent); font-weight: 600; font-size: 0.88rem; white-space: nowrap; }
  .others-label { font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink-faint); font-weight: 600; margin: 1.25rem 0 0.6rem; }
</style>
