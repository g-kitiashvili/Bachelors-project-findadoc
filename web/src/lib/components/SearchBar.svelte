<script lang="ts">
  import { goto } from "$app/navigation";

  let {
    initialValue = "",
    placeholder = "Search by name, specialty, condition…",
    autofocus = false,
  }: { initialValue?: string; placeholder?: string; autofocus?: boolean } = $props();

  let value = $state(initialValue);

  function submit(event: Event) {
    event.preventDefault();
    const q = value.trim();
    const url = q ? `/doctors?q=${encodeURIComponent(q)}` : "/doctors";
    goto(url);
  }
</script>

<form class="search" onsubmit={submit}>
  <span class="search-icon">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="11" cy="11" r="7" />
      <line x1="16.5" y1="16.5" x2="21" y2="21" />
    </svg>
  </span>
  <input
    type="text"
    {placeholder}
    bind:value
    autofocus={autofocus}
    aria-label="Search doctors"
  />
  <button type="submit" class="search-btn">Search</button>
</form>

<style>
  .search {
    display: flex;
    align-items: stretch;
    background: var(--surface);
    border: 1px solid var(--line-strong);
    border-radius: 10px;
    overflow: hidden;
    transition: border-color 0.15s, box-shadow 0.15s;
    box-shadow: 0 1px 2px rgba(14, 19, 32, 0.04);
  }
  .search:focus-within {
    border-color: var(--accent);
    box-shadow: 0 0 0 4px var(--accent-soft);
  }
  .search-icon {
    display: flex;
    align-items: center;
    padding-left: 1.1rem;
    color: var(--ink-faint);
  }
  input {
    flex: 1;
    border: none;
    outline: none;
    background: transparent;
    font-size: 1.05rem;
    color: var(--ink);
    padding: 1.1rem 1rem;
    min-width: 0;
  }
  input::placeholder {
    color: var(--ink-faint);
  }
  .search-btn {
    border: none;
    background: var(--accent);
    color: white;
    padding: 0 1.6rem;
    font-size: 0.92rem;
    font-weight: 600;
    transition: background 0.15s;
    white-space: nowrap;
  }
  .search-btn:hover {
    background: var(--accent-deep);
  }
</style>
