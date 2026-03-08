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
  <nav class="pagination">
    <a
      href={prevDisabled ? null : `?page=${page - 1}`}
      class:disabled={prevDisabled}
      aria-disabled={prevDisabled}>
      &lt; Prev
    </a>
    <span class="status">Page {page} of {totalPages}</span>
    <a
      href={nextDisabled ? null : `?page=${page + 1}`}
      class:disabled={nextDisabled}
      aria-disabled={nextDisabled}>
      Next &gt;
    </a>
  </nav>
{/if}

<style>
  .pagination {
    display: flex;
    gap: 1rem;
    align-items: center;
    justify-content: center;
    margin: 2rem 0;
  }
  .pagination a {
    text-decoration: none;
    padding: 0.4rem 0.8rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    color: #333;
  }
  .pagination a.disabled {
    color: #aaa;
    pointer-events: none;
    background: #f5f5f5;
  }
  .status { color: #555; }
</style>
