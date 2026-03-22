<script lang="ts">
  let {
    page,
    pageSize,
    total,
  }: { page: number; pageSize: number; total: number } = $props();

  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const prevDisabled = page <= 1;
  const nextDisabled = page >= totalPages;
</script>

{#if total > 0}
  <nav class="pagination" aria-label="Pagination">
    <a
      href={prevDisabled ? null : `?page=${page - 1}`}
      class:disabled={prevDisabled}
      aria-disabled={prevDisabled}>
      ← Prev
    </a>
    <span class="status">Page {page} of {totalPages}</span>
    <a
      href={nextDisabled ? null : `?page=${page + 1}`}
      class:disabled={nextDisabled}
      aria-disabled={nextDisabled}>
      Next →
    </a>
  </nav>
{/if}

<style>
  .pagination {
    display: flex;
    gap: 0.75rem;
    align-items: center;
    justify-content: center;
    margin: 2.5rem 0 1rem;
  }
  .pagination a {
    padding: 0.55rem 1rem;
    border: 1px solid var(--line);
    border-radius: 8px;
    color: var(--ink);
    font-size: 0.92rem;
    font-weight: 500;
    transition: all 0.15s;
    background: var(--surface);
  }
  .pagination a:not(.disabled):hover {
    border-color: var(--accent);
    color: var(--accent);
    background: var(--accent-soft);
  }
  .pagination a.disabled {
    color: var(--ink-faint);
    pointer-events: none;
    background: var(--bg-soft);
  }
  .status {
    color: var(--ink-muted);
    font-size: 0.92rem;
    font-weight: 500;
    margin: 0 0.5rem;
  }
</style>
