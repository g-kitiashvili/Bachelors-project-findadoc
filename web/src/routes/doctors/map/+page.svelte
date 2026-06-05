<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  import FilterBar from "$lib/components/FilterBar.svelte";
  import SearchBar from "$lib/components/SearchBar.svelte";
  import * as m from "$lib/paraglide/messages";
  import { href, localizedField } from "$lib/i18n";
  import { getLocale } from "$lib/paraglide/runtime";
  import "leaflet/dist/leaflet.css";
  import "leaflet.markercluster/dist/MarkerCluster.css";
  import "leaflet.markercluster/dist/MarkerCluster.Default.css";

  let { data } = $props();
  let mapEl: HTMLDivElement;
  let locating = $state(false);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let map: any = null;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let leaflet: any = null;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let clusterLayer: any = null;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let meLayer: any = null;

  function escapeHtml(s: string): string {
    return s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c] as string));
  }

  function useMyLocation() {
    if (!navigator.geolocation) return;
    locating = true;
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const url = new URL($page.url);
        url.searchParams.set("center", `${pos.coords.latitude},${pos.coords.longitude}`);
        url.searchParams.set("radiusKm", "10");
        url.searchParams.set("me", "1");
        url.searchParams.delete("focus");
        goto(url.pathname + url.search);
        locating = false;
      },
      () => { locating = false; },
      { enableHighAccuracy: true, timeout: 10000 },
    );
  }

  function renderPins() {
    if (!map || !leaflet) return;
    const L = leaflet;
    if (clusterLayer) { map.removeLayer(clusterLayer); clusterLayer = null; }
    if (meLayer) { map.removeLayer(meLayer); meLayer = null; }

    clusterLayer = L.markerClusterGroup();
    const icon = L.divIcon({ className: "pin-icon", html: "<span></span>", iconSize: [18, 18] });
    const bounds: [number, number][] = [];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let focusMarker: any = null;

    for (const p of data.pins) {
      const marker = L.marker([p.lat, p.lng], { icon });
      const pinName = localizedField(p.nameKa, p.nameEn, getLocale());
      marker.bindTooltip(pinName, { direction: "top" });
      const docs = `${p.doctorCount} ${p.doctorCount === 1 ? m.noun_doctor() : m.noun_doctors()}`;
      marker.bindPopup(
        `<strong>${escapeHtml(pinName)}</strong><br>${docs}<br>` +
        `<a href="${escapeHtml(href(`/clinics/${encodeURIComponent(p.slug)}`))}">${m.map_view_clinic()}</a>`,
      );
      clusterLayer.addLayer(marker);
      bounds.push([p.lat, p.lng]);
      if (data.focus && p.slug === data.focus) focusMarker = marker;
    }
    map.addLayer(clusterLayer);

    if (data.isMyLocation && data.centerPoint) {
      const meIcon = L.divIcon({ className: "me-icon", html: "<span></span>", iconSize: [22, 22] });
      meLayer = L.layerGroup([
        L.marker([data.centerPoint.lat, data.centerPoint.lng], { icon: meIcon, zIndexOffset: 1000 }).bindTooltip(m.map_you_are_here(), { direction: "top" }),
        L.circle([data.centerPoint.lat, data.centerPoint.lng], {
          radius: (data.radiusKm ?? 10) * 1000, color: "#2563eb", weight: 1, fillColor: "#2563eb", fillOpacity: 0.06,
        }),
      ]).addTo(map);
      map.setView([data.centerPoint.lat, data.centerPoint.lng], 12);
    } else if (data.centerPoint) {
      map.setView([data.centerPoint.lat, data.centerPoint.lng], 15);
      if (focusMarker) clusterLayer.zoomToShowLayer(focusMarker, () => focusMarker.openPopup());
    } else if (bounds.length > 0) {
      map.fitBounds(bounds, { padding: [40, 40] });
    }
  }

  onMount(() => {
    // onMount must return its cleanup synchronously, so the async map setup runs in an IIFE.
    (async () => {
      leaflet = (await import("leaflet")).default;
      await import("leaflet.markercluster");
      map = leaflet.map(mapEl).setView([41.7151, 44.8271], 12); // Tbilisi
      leaflet.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(map);
      // Container size isn't final at init under flex/grid layout; recompute so tiles fill it.
      setTimeout(() => map?.invalidateSize(), 0);
      renderPins();
    })();
    return () => { map?.remove(); map = null; };
  });

  $effect(() => {
    void data.pins;
    if (map) renderPins();
  });
</script>

<svelte:head><title>{m.meta_map()}</title></svelte:head>

<div class="map-head">
  <div class="bar">
    <h1>{m.map_heading()}</h1>
    <div class="view-toggle">
      <a class="seg" href={`${href('/doctors')}${data.query}`}>{m.doctors_view_list()}</a>
      <span class="seg active" aria-current="page">{m.doctors_view_map()}</span>
    </div>
  </div>

  <div class="toolbar">
    <div class="search-row">
      <SearchBar mapMode initialValue={data.q} />
    </div>
    <div class="controls">
      <FilterBar
        selectedSlugs={data.selectedSlugs}
        specialties={data.specialties}
        regions={data.regions}
        selectedRegion={data.selectedRegion}
        selectedCity={data.selectedCity}
        clinics={data.clinics}
        selectedClinics={data.selectedClinics}
        selectedTreatsChildren={data.selectedTreatsChildren}
        selectedTreatsAdults={data.selectedTreatsAdults}
      />
      <button type="button" class="locate" onclick={useMyLocation} disabled={locating}>
        {locating ? m.map_locating() : m.map_near_me()}
      </button>
    </div>
  </div>

  <p class="note">
    <span class="count">{data.isMyLocation ? m.map_count_near({ count: data.pins.length }) : m.map_count_all({ count: data.pins.length })}</span>
    <span class="hint">{m.map_note()}</span>
  </p>
</div>

<div class="map" bind:this={mapEl}></div>

<style>
  .map-head { max-width: 1280px; margin: 2rem auto 0; padding: 0 2rem; }
  .bar { display: flex; align-items: baseline; justify-content: space-between; gap: 1rem; margin-bottom: 1.25rem; }
  h1 { font-family: var(--display); font-size: 1.8rem; letter-spacing: -0.02em; margin: 0; }
  .view-toggle {
    display: inline-flex;
    border: 1px solid var(--line-strong);
    border-radius: 8px;
    overflow: hidden;
    flex-shrink: 0;
  }
  .seg {
    padding: 0.45rem 0.9rem;
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--ink-muted);
    background: var(--surface);
    white-space: nowrap;
  }
  .seg + .seg { border-left: 1px solid var(--line-strong); }
  a.seg:hover { color: var(--accent); background: var(--accent-soft); }
  .seg.active { background: var(--accent); color: white; }

  /* One aligned control bar: search grows but is capped; Filters + Near me sit beside it. */
  .toolbar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
  }
  .search-row { flex: 1 1 320px; max-width: 460px; min-width: 0; }
  .controls {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
  }
  /* FilterBar is built as its own full-width row; strip that so it aligns inside the toolbar. */
  .controls :global(.bar) { margin: 0; padding: 0; max-width: none; }

  .locate {
    border: 1px solid var(--line-strong);
    background: var(--surface);
    color: var(--ink);
    padding: 0.55rem 1rem;
    border-radius: 100px;
    font-size: 0.88rem;
    font-weight: 600;
    white-space: nowrap;
    cursor: pointer;
    transition: border-color 0.15s, color 0.15s;
  }
  .locate:hover:not(:disabled) { border-color: var(--accent); color: var(--accent); }
  .locate:disabled { opacity: 0.6; cursor: progress; }

  .note {
    display: flex;
    align-items: baseline;
    gap: 0.5rem 0.85rem;
    flex-wrap: wrap;
    margin: 0.9rem 0 0;
    font-size: 0.85rem;
  }
  .note .count { font-weight: 600; color: var(--ink); }
  .note .hint { color: var(--ink-faint); }

  .map {
    max-width: 1280px;
    height: 66vh;
    margin: 1.25rem auto 3rem;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--line);
    position: relative;
    z-index: 0;
    isolation: isolate; /* contain Leaflet's high pane/control z-indexes below the filter UI */
  }
  :global(.pin-icon span) {
    display: block; width: 14px; height: 14px; border-radius: 50%;
    background: var(--accent); border: 2px solid white; box-shadow: 0 1px 4px rgba(14, 19, 32, 0.4);
  }
  :global(.me-icon span) {
    display: block; width: 16px; height: 16px; border-radius: 50%;
    background: #2563eb; border: 3px solid white; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.3);
  }
</style>
