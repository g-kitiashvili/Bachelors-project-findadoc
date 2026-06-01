import { describe, it, expect } from 'vitest';
import {
  initState, advance, back, toggleSymptom, submit, score,
  type TriageGraph,
} from './triage';

const graph: TriageGraph = {
  start: 'a',
  nodes: {
    a: { question: { ka: 'ა', en: 'A' }, options: [
      { label: { ka: 'შ', en: 'to-symptoms' }, next: 's' },
      { label: { ka: 'შ', en: 'direct' }, result: { type: 'specialty', slug: 'dentistry' } },
    ] },
    s: { question: { ka: 'ს', en: 'S' }, symptoms: [
      { label: { ka: '1', en: 'one' }, weights: { 'specialty:neurology': 3, 'condition:migraine': 2 } },
      { label: { ka: '2', en: 'two' }, weights: { 'specialty:neurology': 2, 'specialty:ent': 2 } },
      { label: { ka: '3', en: 'three' }, weights: { 'condition:migraine': 1 } },
    ] },
  },
};

describe('triage traversal', () => {
  it('starts at the start node with empty history and no ranking', () => {
    const st = initState(graph);
    expect(st.currentId).toBe('a');
    expect(st.history).toEqual([]);
    expect(st.selected).toEqual([]);
    expect(st.ranked).toBeNull();
  });
  it('advance on a next-option moves on and records history', () => {
    const st = advance(graph, initState(graph), graph.nodes.a.options![0]);
    expect(st.currentId).toBe('s');
    expect(st.history).toEqual(['a']);
    expect(st.ranked).toBeNull();
  });
  it('advance on a direct result-option ranks that single slug', () => {
    const st = advance(graph, initState(graph), graph.nodes.a.options![1]);
    expect(st.ranked).toEqual([{ type: 'specialty', slug: 'dentistry', score: 1 }]);
  });
  it('toggleSymptom adds then removes an index', () => {
    let st = advance(graph, initState(graph), graph.nodes.a.options![0]);
    st = toggleSymptom(st, 0);
    expect(st.selected).toEqual([0]);
    st = toggleSymptom(st, 0);
    expect(st.selected).toEqual([]);
  });
  it('back from a symptom screen clears selections and returns', () => {
    let st = advance(graph, initState(graph), graph.nodes.a.options![0]);
    st = toggleSymptom(st, 1);
    st = back(st);
    expect(st.currentId).toBe('a');
    expect(st.selected).toEqual([]);
    expect(st.ranked).toBeNull();
  });
});

describe('score', () => {
  it('returns empty for a node with no symptoms', () => {
    expect(score(graph.nodes.a, [0])).toEqual([]);
  });
  it('returns empty when nothing is selected', () => {
    expect(score(graph.nodes.s, [])).toEqual([]);
  });
  it('sums weights across selected symptoms and ranks descending', () => {
    const r = score(graph.nodes.s, [0, 2]);
    expect(r).toEqual([
      { type: 'specialty', slug: 'neurology', score: 3 },
      { type: 'condition', slug: 'migraine', score: 3 },
    ]);
  });
  it('ranks the strongest destination first', () => {
    const r = score(graph.nodes.s, [0, 1]);
    expect(r[0]).toEqual({ type: 'specialty', slug: 'neurology', score: 5 });
    expect(r.map((x) => x.slug)).toEqual(['neurology', 'migraine', 'ent']);
  });
  it('breaks ties by first appearance in the YAML', () => {
    const r = score(graph.nodes.s, [1]);
    expect(r.map((x) => x.slug)).toEqual(['neurology', 'ent']);
  });
});

describe('submit', () => {
  it('stores the top 3 ranked results', () => {
    let st = advance(graph, initState(graph), graph.nodes.a.options![0]);
    st = toggleSymptom(st, 0);
    st = toggleSymptom(st, 1);
    st = submit(graph, st);
    expect(st.ranked!.length).toBeLessThanOrEqual(3);
    expect(st.ranked![0].slug).toBe('neurology');
  });
});
