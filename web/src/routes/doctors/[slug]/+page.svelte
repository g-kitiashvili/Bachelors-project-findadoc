<script lang="ts">
  import DoctorProfile from "$lib/components/DoctorProfile.svelte";
  import SimilarDoctors from "$lib/components/SimilarDoctors.svelte";

  let { data } = $props();
</script>

<svelte:head>
  <title>{data.doctor.fullNameEn} — Find-a-Doc</title>
</svelte:head>

<nav class="breadcrumb" aria-label="Breadcrumb">
  <div class="breadcrumb-inner">
    <a href="/doctors">← All doctors</a>
  </div>
</nav>

<DoctorProfile doctor={data.doctor} />

<SimilarDoctors doctors={data.similar} />

<style>
  .breadcrumb {
    border-bottom: 1px solid var(--line);
    background: var(--bg-soft);
  }
  .breadcrumb-inner {
    max-width: 1280px;
    margin: 0 auto;
    padding: 1rem 2rem;
  }
  .breadcrumb a {
    color: var(--ink-muted);
    font-size: 0.92rem;
    font-weight: 500;
    transition: color 0.15s;
  }
  .breadcrumb a:hover {
    color: var(--accent);
  }
  @media (max-width: 600px) {
    .breadcrumb-inner { padding: 1rem 1.25rem; }
  }
</style>
