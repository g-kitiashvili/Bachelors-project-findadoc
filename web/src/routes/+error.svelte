<script lang="ts">
  import { page } from "$app/state";
  import * as m from "$lib/paraglide/messages";
  import { href } from "$lib/i18n";
</script>

<svelte:head>
  <title>{m.meta_not_found()}</title>
</svelte:head>

<section class="error">
  <div class="eyebrow">{page.status === 404 ? m.error_404_title() : m.error_generic_title({ status: page.status })}</div>
  <h1>{page.status === 404 ? m.error_page_not_found() : m.error_something_wrong()}</h1>
  <p class="detail">{page.error?.message ?? m.error_default_message()}</p>
  <a class="back" href={href("/")}>{m.error_back_home()}</a>
</section>

<style>
  .error {
    max-width: 640px;
    margin: 5rem auto 4rem;
    padding: 3rem 2rem;
    text-align: center;
    background: var(--bg-soft);
    border: 1px solid var(--line);
    border-radius: 16px;
  }
  .eyebrow {
    color: var(--accent);
    font-size: 0.82rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 1rem;
  }
  h1 {
    font-family: var(--display);
    font-weight: 600;
    font-size: 1.8rem;
    letter-spacing: -0.02em;
    color: var(--ink);
    margin: 0 0 1rem;
  }
  .detail {
    color: var(--ink-muted);
    margin: 0 0 2rem;
    line-height: 1.55;
  }
  .back {
    display: inline-block;
    background: var(--ink);
    color: white;
    padding: 0.7rem 1.4rem;
    border-radius: 8px;
    font-size: 0.92rem;
    font-weight: 500;
    transition: background 0.15s;
  }
  .back:hover {
    background: var(--accent);
  }
  @media (max-width: 600px) {
    .error {
      margin: 3rem 1.25rem;
      padding: 2.5rem 1.5rem;
    }
  }
</style>
