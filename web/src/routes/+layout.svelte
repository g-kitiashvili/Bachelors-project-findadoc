<script lang="ts">
  import "../app.css";
  import TopNav from "$lib/components/TopNav.svelte";
  import SiteFooter from "$lib/components/SiteFooter.svelte";
  import { page } from "$app/state";

  let { children } = $props();

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

<TopNav {active} />
<div class="content">
  {@render children()}
</div>
<SiteFooter />

<style>
  .content {
    min-height: calc(100vh - 12rem);
  }
</style>
