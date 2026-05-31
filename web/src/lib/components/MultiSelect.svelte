<script lang="ts">
  import { tick } from "svelte";
  import * as m from "$lib/paraglide/messages";

  interface Option { value: string; label: string; count?: number }

  interface Props {
    placeholder: string;
    options: Option[];
    selected: string[];
    label?: string;
    multiple?: boolean;
    searchable?: boolean;
    searchPlaceholder?: string;
    compact?: boolean;
    onChange: (next: string[]) => void;
  }

  let {
    placeholder,
    options,
    selected,
    label,
    multiple = true,
    searchable = true,
    searchPlaceholder = m.multiselect_search(),
    compact = false,
    onChange,
  }: Props = $props();

  let open = $state(false);
  let query = $state("");
  let root: HTMLDivElement;
  let searchEl = $state<HTMLInputElement>();

  const selectedSet = $derived(new Set(selected));
  const labelByValue = $derived(new Map(options.map((o) => [o.value, o.label])));
  const summary = $derived(selected.map((v) => labelByValue.get(v) ?? v).join(", "));

  const visible = $derived(
    query.trim() === ""
      ? options
      : options.filter((o) => o.label.toLowerCase().includes(query.trim().toLowerCase())),
  );

  function toggleMenu() {
    open = !open;
    if (open) query = "";
  }

  function choose(value: string) {
    if (multiple) {
      onChange(selectedSet.has(value) ? selected.filter((v) => v !== value) : [...selected, value]);
    } else {
      onChange(value === "" ? [] : [value]);
      open = false;
    }
  }

  $effect(() => {
    if (!open) return;
    tick().then(() => searchEl?.focus());
    function onDocClick(e: MouseEvent) {
      if (root && !root.contains(e.target as Node)) open = false;
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") open = false;
    }
    document.addEventListener("mousedown", onDocClick);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDocClick);
      document.removeEventListener("keydown", onKey);
    };
  });
</script>

<div class="ms" class:open class:multi={multiple} bind:this={root}>
  {#if label}<div class="ms-label">{label}</div>{/if}

  <button type="button" class="ms-control" class:compact aria-haspopup="listbox" aria-expanded={open} onclick={toggleMenu}>
    <span class="ms-value" class:placeholder={selected.length === 0}>
      {selected.length === 0 ? placeholder : summary}
    </span>
    <svg class="ms-chevron" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
    </svg>
  </button>

  {#if open}
    <div class="ms-pop" role="listbox" aria-multiselectable={multiple}>
      {#if searchable}
        <div class="ms-search">
          <svg class="ms-search-icon" viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <circle cx="7" cy="7" r="4.5" stroke="currentColor" stroke-width="1.5" />
            <path d="M11 11l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
          </svg>
          <input bind:this={searchEl} bind:value={query} placeholder={searchPlaceholder} type="text" />
        </div>
      {/if}
      <ul class="ms-list">
        {#each visible as o (o.value)}
          {@const isSel = selectedSet.has(o.value)}
          <li>
            <button type="button" class="ms-option" class:selected={isSel} role="option" aria-selected={isSel} onclick={() => choose(o.value)}>
              {#if multiple}<span class="ms-check" aria-hidden="true"></span>{/if}
              <span class="ms-opt-label">{o.label}</span>
              {#if o.count !== undefined}<span class="ms-count">{o.count}</span>{/if}
              {#if !multiple && isSel}<span class="ms-tick" aria-hidden="true">✓</span>{/if}
            </button>
          </li>
        {:else}
          <li class="ms-empty">{m.search_no_matches()}</li>
        {/each}
      </ul>
    </div>
  {/if}
</div>

<style>
  .ms { position: relative; width: 100%; }
  .ms.open { z-index: 30; }

  .ms-label {
    font-size: 0.7rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.05em; color: var(--ink-muted); margin-bottom: 0.4rem;
  }

  .ms-control {
    width: 100%; display: flex; align-items: center; justify-content: space-between; gap: 0.5rem;
    padding: 0.6rem 0.8rem; border: 1px solid var(--line); border-radius: 8px;
    background: var(--surface); color: var(--ink); text-align: left;
    transition: border-color 0.15s, box-shadow 0.15s;
  }
  .ms-control:hover { border-color: var(--line-strong); }
  .ms.open .ms-control { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }
  .ms-control.compact { padding: 0.4rem 0.6rem; border-radius: 7px; }

  .ms-value {
    flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    font-size: 0.92rem;
  }
  .ms-control.compact .ms-value { font-size: 0.85rem; }
  .ms-value.placeholder { color: var(--ink-faint); }

  .ms-chevron { width: 16px; height: 16px; color: var(--ink-muted); flex-shrink: 0; transition: transform 0.18s ease; }
  .ms.open .ms-chevron { transform: rotate(180deg); }

  .ms-pop {
    position: absolute; top: calc(100% + 6px); left: 0; right: 0; z-index: 40;
    background: var(--surface); border: 1px solid var(--line); border-radius: 10px;
    box-shadow: 0 12px 28px rgba(14, 19, 32, 0.12); padding: 6px;
  }

  .ms-search { position: relative; margin: 2px 2px 6px; }
  .ms-search-icon {
    position: absolute; left: 0.6rem; top: 50%; transform: translateY(-50%);
    width: 15px; height: 15px; color: var(--ink-faint); pointer-events: none;
  }
  .ms-search input {
    width: 100%; padding: 0.5rem 0.6rem 0.5rem 2rem; border: 1px solid var(--line);
    border-radius: 8px; font: inherit; font-size: 0.9rem; color: var(--ink);
  }
  .ms-search input:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }

  .ms-list { list-style: none; margin: 0; padding: 0; max-height: 264px; overflow-y: auto; }

  .ms-option {
    width: 100%; display: flex; align-items: center; gap: 0.6rem; padding: 0.5rem 0.6rem;
    border: 0; background: none; border-radius: 7px; text-align: left;
    font-size: 0.92rem; color: var(--ink);
  }
  .ms-option:hover { background: var(--bg-soft); }
  .ms:not(.multi) .ms-option.selected { color: var(--accent); font-weight: 500; }

  .ms-opt-label { flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .ms-count { color: var(--ink-faint); font-size: 0.8rem; font-variant-numeric: tabular-nums; }
  .ms-tick { color: var(--accent); font-size: 0.85rem; }

  .ms-check {
    width: 18px; height: 18px; flex-shrink: 0; position: relative;
    border: 1.5px solid var(--line-strong); border-radius: 5px; transition: background 0.12s, border-color 0.12s;
  }
  .ms-option.selected .ms-check { background: var(--accent); border-color: var(--accent); }
  .ms-option.selected .ms-check::after {
    content: ""; position: absolute; left: 5px; top: 1px; width: 5px; height: 9px;
    border: solid white; border-width: 0 2px 2px 0; transform: rotate(45deg);
  }

  .ms-empty { padding: 0.7rem; color: var(--ink-faint); font-size: 0.88rem; text-align: center; }
</style>
