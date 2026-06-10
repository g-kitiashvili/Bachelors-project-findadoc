<script lang="ts">
  import DoctorProfile from "$lib/components/DoctorProfile.svelte";
  import SimilarDoctors from "$lib/components/SimilarDoctors.svelte";
  import * as m from "$lib/paraglide/messages";
  import { href, localizedField } from "$lib/i18n";
  import { getLocale } from "$lib/paraglide/runtime";
  import { jsonLdScript } from "$lib/jsonld";
  import { page } from "$app/state";

  let { data } = $props();

  const ld = $derived.by(() => {
    const d = data.doctor;
    const loc = getLocale();
    return jsonLdScript({
      "@type": "Physician",
      name: localizedField(d.fullNameKa, d.fullNameEn, loc),
      url: page.url.origin + page.url.pathname,
      ...(d.photoUrl ? { image: d.photoUrl } : {}),
      ...(d.specialties?.length
        ? { medicalSpecialty: d.specialties.map((s) => localizedField(s.nameKa, s.nameEn, loc)) }
        : {}),
      ...(d.clinics?.length
        ? { worksFor: d.clinics.map((c) => ({ "@type": "MedicalClinic", name: localizedField(c.nameKa, c.nameEn, loc) })) }
        : {}),
    });
  });
</script>

<svelte:head>
  <title>{localizedField(data.doctor.fullNameKa, data.doctor.fullNameEn, getLocale())}{m.meta_suffix()}</title>
  {@html ld}
</svelte:head>

<nav class="breadcrumb" aria-label={m.aria_breadcrumb()}>
  <div class="breadcrumb-inner">
    <a href={href("/doctors")}>{m.back_all_doctors()}</a>
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
