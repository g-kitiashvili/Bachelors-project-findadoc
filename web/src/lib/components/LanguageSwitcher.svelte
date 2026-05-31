<script lang="ts">
  import { page } from '$app/state';
  import * as m from '$lib/paraglide/messages';
  import { localizeHref, deLocalizeHref, getLocale } from '$lib/paraglide/runtime';

  const locales = [
    { code: 'ka', label: 'ქარ' },
    { code: 'en', label: 'EN' }
  ] as const;

  // Full navigation (not SPA goto): Paraglide's compiled messages only re-evaluate on a
  // server render, so the new locale must come from a real page load of the localized URL.
  function switchTo(locale: 'ka' | 'en') {
    if (locale === getLocale()) return;
    document.cookie = `PARAGLIDE_LOCALE=${locale}; path=/; max-age=31536000`;
    window.location.href = localizeHref(deLocalizeHref(page.url.pathname), { locale }) + page.url.search;
  }
</script>

<div class="lang" role="group" aria-label={m.aria_language()}>
  {#each locales as l (l.code)}
    <button type="button" class:active={getLocale() === l.code} onclick={() => switchTo(l.code)}>
      {l.label}
    </button>
  {/each}
</div>

<style>
  .lang { display: inline-flex; border: 1px solid var(--line-strong); border-radius: 8px; overflow: hidden; }
  .lang button { padding: 0.4rem 0.7rem; font-size: 0.82rem; font-weight: 600; color: var(--ink-muted); background: var(--surface); }
  .lang button + button { border-left: 1px solid var(--line-strong); }
  .lang button:hover { color: var(--accent); background: var(--accent-soft); }
  .lang button.active { background: var(--accent); color: white; }
</style>
