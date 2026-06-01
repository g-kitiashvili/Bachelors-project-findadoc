export interface TriageResult { type: 'specialty' | 'condition'; slug: string }
export interface LocalizedText { ka: string; en: string }
export interface TriageOption { label: LocalizedText; next?: string; result?: TriageResult }
export interface TriageSymptom { label: LocalizedText; weights: Record<string, number> }
export interface TriageNode { question: LocalizedText; options?: TriageOption[]; symptoms?: TriageSymptom[] }
export interface TriageGraph { start: string; nodes: Record<string, TriageNode> }

export interface ScoredResult { type: 'specialty' | 'condition'; slug: string; score: number }
export interface TriageState {
  currentId: string;
  history: string[];
  selected: number[];
  ranked: ScoredResult[] | null;
}

const MAX_RESULTS = 3;

export function initState(graph: TriageGraph): TriageState {
  return { currentId: graph.start, history: [], selected: [], ranked: null };
}

export function advance(graph: TriageGraph, state: TriageState, option: TriageOption): TriageState {
  if (option.result) {
    return { ...state, ranked: [{ ...option.result, score: 1 }] };
  }
  if (option.next && graph.nodes[option.next]) {
    return { currentId: option.next, history: [...state.history, state.currentId], selected: [], ranked: null };
  }
  return state;
}

export function toggleSymptom(state: TriageState, index: number): TriageState {
  const selected = state.selected.includes(index)
    ? state.selected.filter((i) => i !== index)
    : [...state.selected, index];
  return { ...state, selected };
}

export function score(node: TriageNode, selected: number[]): ScoredResult[] {
  if (!node.symptoms) return [];
  const totals = new Map<string, number>();
  const order: string[] = [];
  for (const i of selected) {
    const sym = node.symptoms[i];
    if (!sym) continue;
    for (const [key, w] of Object.entries(sym.weights)) {
      if (!totals.has(key)) order.push(key);
      totals.set(key, (totals.get(key) ?? 0) + w);
    }
  }
  return order
    .map((key, idx) => {
      const [type, slug] = key.split(':') as ['specialty' | 'condition', string];
      return { type, slug, score: totals.get(key)!, idx };
    })
    .sort((a, b) => b.score - a.score || a.idx - b.idx)
    .filter((r) => r.score > 0)
    .map(({ type, slug, score }) => ({ type, slug, score }));
}

export function submit(graph: TriageGraph, state: TriageState): TriageState {
  const node = graph.nodes[state.currentId];
  const ranked = score(node, state.selected).slice(0, MAX_RESULTS);
  return { ...state, ranked: ranked.length ? ranked : null };
}

export function back(state: TriageState): TriageState {
  if (state.history.length === 0) {
    return { ...state, selected: [], ranked: null };
  }
  const history = [...state.history];
  const currentId = history.pop()!;
  return { currentId, history, selected: [], ranked: null };
}
