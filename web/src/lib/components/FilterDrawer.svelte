<script lang="ts">
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";

  interface Props {
    open: boolean;
    selectedSlugs: string[];
    specialties: Array<{ slug: string; nameEn: string; nameKa: string; doctorCount: number }>;
    onClose: () => void;
  }

  let { open, selectedSlugs, specialties, onClose }: Props = $props();

  let draft = $state<string[]>([...selectedSlugs]);
  let search = $state("");

  $effect(() => {
    draft = [...selectedSlugs];
  });

  const filtered = $derived(
    search.trim() === ""
      ? specialties
      : specialties.filter((s) =>
          s.nameEn.toLowerCase().includes(search.toLowerCase()) ||
          s.nameKa.includes(search)
        )
  );

  function toggle(slug: string) {
    if (draft.includes(slug)) {
      draft = draft.filter((s) => s !== slug);
    } else {
      draft = [...draft, slug];
    }
  }

  function apply() {
    const url = new URL($page.url);
    if (draft.length > 0) {
      url.searchParams.set("specialty", draft.join(","));
    } else {
      url.searchParams.delete("specialty");
    }
    url.searchParams.delete("page");
    goto(url.pathname + url.search);
    onClose();
  }

  function clearDraft() {
    draft = [];
  }
</script>

{#if open}
  <div class="backdrop" onclick={onClose} role="presentation"></div>
  <aside class="drawer" role="dialog" aria-label="Filters">
    <header>
      <h2>Filters</h2>
      <button class="close" onclick={onClose} aria-label="Close">✕</button>
    </header>

    <div class="section">
      <div class="label">Specialty</div>
      <input
        class="search"
        type="text"
        placeholder="Search specialties..."
        bind:value={search}
      />
      <ul class="checklist">
        {#each filtered as s (s.slug)}
          <li>
            <label>
              <input
                type="checkbox"
                checked={draft.includes(s.slug)}
                onchange={() => toggle(s.slug)}
              />
              <span class="name">{s.nameEn}</span>
              <span class="count">({s.doctorCount})</span>
            </label>
          </li>
        {/each}
      </ul>
    </div>

    <footer>
      <button class="apply" onclick={apply}>Apply ({draft.length})</button>
      <button class="clear" onclick={clearDraft}>Clear</button>
    </footer>
  </aside>
{/if}

<style>
  .backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.35); z-index: 40; }
  .drawer { position: fixed; top: 0; left: 0; bottom: 0; width: 360px; background: white; z-index: 50; display: flex; flex-direction: column; box-shadow: 2px 0 16px rgba(0,0,0,0.1); }
  header { display: flex; justify-content: space-between; align-items: center; padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--line); }
  header h2 { font-family: var(--display); font-size: 1.25rem; margin: 0; }
  .close { background: none; border: 0; font-size: 1.25rem; cursor: pointer; color: var(--ink-muted); }
  .section { flex: 1; overflow-y: auto; padding: 1.25rem 1.5rem; }
  .label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--ink-muted); margin-bottom: 0.75rem; }
  .search { width: 100%; padding: 0.55rem 0.75rem; border: 1px solid var(--line); border-radius: 6px; margin-bottom: 0.75rem; font: inherit; }
  .checklist { list-style: none; margin: 0; padding: 0; }
  .checklist li { margin-bottom: 0.4rem; }
  .checklist label { display: flex; gap: 0.6rem; align-items: center; cursor: pointer; font-size: 0.9rem; }
  .checklist .name { flex: 1; }
  .checklist .count { color: var(--ink-faint); font-size: 0.8rem; }
  footer { display: flex; gap: 0.75rem; padding: 1.25rem 1.5rem; border-top: 1px solid var(--line); }
  .apply { flex: 1; background: var(--accent); color: white; border: 0; padding: 0.7rem; border-radius: 6px; font: inherit; font-weight: 600; cursor: pointer; }
  .clear { background: none; border: 1px solid var(--line); padding: 0.7rem 1rem; border-radius: 6px; font: inherit; cursor: pointer; color: var(--ink); }
</style>
