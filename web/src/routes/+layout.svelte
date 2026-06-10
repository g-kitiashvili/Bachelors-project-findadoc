<script lang="ts">
  import "../app.css";
  import TopNav from "$lib/components/TopNav.svelte";
  import SiteFooter from "$lib/components/SiteFooter.svelte";
  import { page } from "$app/state";
  import { localizeHref, deLocalizeHref } from "$lib/paraglide/runtime";

  let { children } = $props();

  // Canonical (current locale) + hreflang alternates, from the locale-stripped path.
  const bare = $derived(deLocalizeHref(page.url.pathname));
  const canonical = $derived(page.url.origin + localizeHref(bare));
  const kaHref = $derived(page.url.origin + localizeHref(bare, { locale: "ka" }));
  const enHref = $derived(page.url.origin + localizeHref(bare, { locale: "en" }));

  // Determine which nav item is active based on the route id.
  const active = $derived.by(() => {
    const id = page.route.id ?? "";
    if (id.startsWith("/doctors/map")) return "map";
    if (id.startsWith("/doctors")) return "doctors";
    if (id.startsWith("/specialties")) return "specialties";
    if (id.startsWith("/conditions")) return "conditions";
    if (id.startsWith("/clinics")) return "clinics";
    if (id.startsWith("/symptoms") || id.startsWith("/body") || id.startsWith("/triage")) return "symptoms";
    if (id.startsWith("/about")) return "about";
    return "";
  });
</script>

<svelte:head>
  <link rel="canonical" href={canonical} />
  <link rel="alternate" hreflang="ka" href={kaHref} />
  <link rel="alternate" hreflang="en" href={enHref} />
  <link rel="alternate" hreflang="x-default" href={enHref} />
</svelte:head>

<TopNav {active} />
<main class="content">
  {@render children()}
</main>
<SiteFooter />

<style>
  .content {
    min-height: calc(100vh - 12rem);
  }
</style>
