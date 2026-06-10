<script lang="ts">
  import * as m from "$lib/paraglide/messages";
  import { href, localizedField } from "$lib/i18n";
  import { getLocale } from "$lib/paraglide/runtime";

  interface SpecialtyRef {
    slug: string;
    nameKa: string;
    nameEn: string;
    isPrimary: boolean;
  }

  interface Doctor {
    slug: string;
    fullNameKa: string;
    fullNameEn: string;
    gender: string | null;
    photoUrl: string | null;
    isAcceptingNewPatients: boolean;
    treatsChildren: boolean;
    treatsAdults: boolean;
    bioKa: string | null;
    bioEn: string | null;
    specialtyKa: string | null;
    specialtyEn: string | null;
    specialties: SpecialtyRef[];
    clinics: Array<{ slug: string; nameKa: string; nameEn: string; address: string | null; addressEn: string | null; phone: string | null }>;
    lastSourceUrl: string | null;
    lastUpdatedAt: string | null;
  }

  let { doctor }: { doctor: Doctor } = $props();

  const SOURCE_NAMES: Record<string, string> = {
    "aversi.ge": "Aversi",
    "tsamali.ge": "Tsamali",
    "cmc.ge": "CMC",
    "caraps.ge": "Caraps",
    "evex.ge": "Evex",
    "vivomedical.ge": "Vivo Medical",
    "vivamedi.ge": "Vivamedi",
    "newhospitals.ge": "New Hospitals",
  };
  function sourceLabel(url: string): string {
    try {
      const host = new URL(url).hostname.replace(/^www\./, "");
      if (SOURCE_NAMES[host]) return SOURCE_NAMES[host];
      const label = host.split(".").slice(-2, -1)[0] ?? host;
      return label.charAt(0).toUpperCase() + label.slice(1);
    } catch {
      return url;
    }
  }
  const source = $derived(
    doctor.lastSourceUrl ? { url: doctor.lastSourceUrl, name: sourceLabel(doctor.lastSourceUrl) } : null,
  );
  const updatedDate = $derived(
    doctor.lastUpdatedAt
      ? new Date(doctor.lastUpdatedAt).toLocaleDateString(getLocale() === "ka" ? "ka-GE" : "en-GB", {
          year: "numeric",
          month: "short",
          day: "numeric",
        })
      : null,
  );

  const name = $derived(localizedField(doctor.fullNameKa, doctor.fullNameEn, getLocale()));
  const specialty = $derived(localizedField(doctor.specialtyKa, doctor.specialtyEn, getLocale()));
  const bio = $derived(localizedField(doctor.bioKa, doctor.bioEn, getLocale()));

  const genderLabel = $derived.by(() => {
    if (doctor.gender === "female") return m.gender_female();
    if (doctor.gender === "male") return m.gender_male();
    return doctor.gender;
  });

  const initial = doctor.fullNameEn.trim().charAt(0).toUpperCase() || "·";

  // Deterministic photo gradient based on slug (matches DoctorCard logic)
  const bgClass = (() => {
    const sum = doctor.slug.split("").reduce((s, c) => s + c.charCodeAt(0), 0);
    const buckets = ["bg-a", "bg-b", "bg-c", "bg-d", "bg-e", "bg-f"] as const;
    return buckets[sum % buckets.length];
  })();

  const treatsLabel = $derived.by(() => {
    const parts: string[] = [];
    if (doctor.treatsAdults) parts.push(m.profile_adults());
    if (doctor.treatsChildren) parts.push(m.profile_children());
    return parts.length ? parts.join(" · ") : "-";
  });
</script>

<section class="profile">
  <aside class="card">
    <div class="photo {bgClass}">
      {#if doctor.photoUrl}
        <img src={doctor.photoUrl} alt="" />
      {:else}
        <span class="initial">{initial}</span>
      {/if}
    </div>
    <div class="card-meta">
      <div class="meta-row">
        <span class="meta-label">{m.profile_treats()}</span>
        <span class="meta-val">{treatsLabel}</span>
      </div>
      {#if doctor.gender}
        <div class="meta-row">
          <span class="meta-label">{m.profile_gender()}</span>
          <span class="meta-val">{genderLabel}</span>
        </div>
      {/if}
      <div class="meta-row">
        <span class="meta-label">{m.profile_accepting()}</span>
        <span class="meta-val" class:success={doctor.isAcceptingNewPatients}>
          {doctor.isAcceptingNewPatients ? m.common_yes() : m.common_no()}
        </span>
      </div>
    </div>
  </aside>

  <div class="body">
    <div class="eyebrow">{m.profile_aria()}</div>
    <h1 class="name">{name}</h1>

    {#if doctor.specialties && doctor.specialties.length > 0}
      <div class="specialty-row">
        {#each doctor.specialties as s (s.slug)}
          <a class="profile-specialty-pill" href={href(`/specialties/${s.slug}`)} class:primary={s.isPrimary}>
            {localizedField(s.nameKa, s.nameEn, getLocale())}
            {#if s.isPrimary}<span class="primary-dot" title={m.profile_primary()}>●</span>{/if}
          </a>
        {/each}
      </div>
    {:else if specialty}
      <div class="specialty-row">
        <span class="profile-specialty-pill profile-specialty-pill--raw">{specialty}</span>
      </div>
    {/if}

    {#if doctor.clinics && doctor.clinics.length > 0}
      <div class="clinic-row">
        {#each doctor.clinics as c (c.slug)}
          <a class="profile-clinic-pill" href={href(`/clinics/${c.slug}`)}>
            {localizedField(c.nameKa, c.nameEn, getLocale())}{#if c.addressEn ?? c.address} · <span class="clinic-addr">{c.addressEn ?? c.address}</span>{/if}
          </a>
          {#if c.phone}<a class="clinic-phone" href={`tel:${c.phone}`}>📞 {c.phone}</a>{/if}
        {/each}
      </div>
    {/if}

    <div class="quick-meta">
      <div class="quick">
        <span class="quick-label">{m.profile_treats()}</span>
        <span class="quick-val">{treatsLabel}</span>
      </div>
      <div class="quick">
        <span class="quick-label">{m.profile_accepting()}</span>
        <span class="quick-val" class:success={doctor.isAcceptingNewPatients}>
          {doctor.isAcceptingNewPatients ? m.common_yes() : m.common_no()}
        </span>
      </div>
    </div>

    <h2 class="bio-head">{m.profile_biography()}</h2>
    <div class="bio">
      {#if bio}
        <p>{bio}</p>
      {:else}
        <p class="empty">{m.profile_no_bio()}</p>
      {/if}
    </div>

    {#if source}
      <p class="source-line">
        {m.profile_source()}: <a href={source.url} target="_blank" rel="noopener noreferrer">{source.name}</a>{#if updatedDate} · {m.profile_updated()} {updatedDate}{/if}
      </p>
    {/if}
  </div>
</section>

<style>
  .profile {
    max-width: 1280px;
    margin: 3rem auto 0;
    padding: 0 2rem;
    display: grid;
    grid-template-columns: 360px 1fr;
    gap: 4rem;
    align-items: start;
  }

  /* sticky meta card */
  .card {
    background: white;
    border: 1px solid var(--line);
    border-radius: 16px;
    overflow: hidden;
    position: sticky;
    top: 6rem;
  }
  .photo {
    aspect-ratio: 1 / 1;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    border-bottom: 1px solid var(--line);
  }
  .photo img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center 25%;
  }
  .photo .initial {
    font-family: var(--display);
    font-weight: 500;
    color: var(--ink);
    font-size: 6rem;
    opacity: 0.85;
  }
  .bg-a { background: linear-gradient(135deg, #f6ebe8, #e8c9c0); }
  .bg-b { background: linear-gradient(135deg, #e5ebf5, #c6d2e6); }
  .bg-c { background: linear-gradient(135deg, #f2ebd7, #d9c895); }
  .bg-d { background: linear-gradient(135deg, #e5f0e8, #bfdbc4); }
  .bg-e { background: linear-gradient(135deg, #f2e7f0, #d5b5cc); }
  .bg-f { background: linear-gradient(135deg, #ecedea, #c8c0be); }

  .card-meta {
    padding: 1.4rem;
    display: flex;
    flex-direction: column;
    gap: 0.9rem;
  }
  .meta-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.88rem;
    gap: 1rem;
  }
  .meta-label {
    color: var(--ink-faint);
    font-weight: 500;
    text-transform: uppercase;
    font-size: 0.74rem;
    letter-spacing: 0.06em;
  }
  .meta-val {
    color: var(--ink);
    font-weight: 500;
    text-align: right;
  }
  .meta-val.accent { color: var(--accent); }
  .meta-val.success { color: var(--success); font-weight: 600; }

  /* right column: body */
  .body { padding-top: 0.5rem; }
  .eyebrow {
    color: var(--accent);
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 1rem;
  }
  .name {
    font-family: var(--display);
    font-weight: 600;
    font-size: clamp(2.2rem, 4vw, 3.2rem);
    line-height: 1.04;
    letter-spacing: -0.025em;
    margin: 0 0 0.6rem;
    color: var(--ink);
  }
  .specialty-row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 1rem 0 1.6rem; }
  .profile-specialty-pill {
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: var(--bg-soft); border: 1px solid var(--line);
    border-radius: 100px; padding: 0.4rem 0.95rem;
    font-size: 0.86rem; color: var(--ink); font-weight: 500;
    text-decoration: none;
    transition: background 0.15s, border-color 0.15s;
  }
  .profile-specialty-pill:hover { background: white; border-color: var(--accent); color: var(--accent); }
  .profile-specialty-pill--raw { color: var(--ink-muted); cursor: default; }
  .profile-specialty-pill--raw:hover { background: var(--bg-soft); border-color: var(--line); color: var(--ink-muted); }
  .primary-dot { color: var(--accent); font-size: 0.6rem; }

  .clinic-row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0 0 1.6rem; }
  .profile-clinic-pill {
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: transparent; border: 1px dashed var(--line-strong);
    border-radius: 100px; padding: 0.4rem 0.95rem;
    font-size: 0.86rem; color: var(--ink-muted); font-weight: 500;
    text-decoration: none;
    transition: background 0.15s, border-color 0.15s, color 0.15s;
  }
  .profile-clinic-pill:hover { background: var(--bg-soft); border-color: var(--ink-muted); color: var(--ink); }
  .clinic-addr { color: var(--ink-faint); font-size: 0.8rem; }
  .clinic-phone {
    display: inline-flex; align-items: center; gap: 0.35rem;
    background: var(--accent-soft); border: 1px solid transparent;
    border-radius: 100px; padding: 0.4rem 0.9rem;
    font-size: 0.86rem; color: var(--accent-deep); font-weight: 600;
    text-decoration: none; white-space: nowrap;
    transition: background 0.15s, color 0.15s;
  }
  .clinic-phone:hover { background: var(--accent); color: white; }

  .quick-meta {
    display: flex;
    gap: 1.5rem;
    padding: 1rem 0;
    border-top: 1px solid var(--line);
    border-bottom: 1px solid var(--line);
    margin-bottom: 2.2rem;
    flex-wrap: wrap;
  }
  .quick {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
  }
  .quick-label {
    font-size: 0.74rem;
    color: var(--ink-faint);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 500;
  }
  .quick-val {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--ink);
  }
  .quick-val.accent { color: var(--accent); }
  .quick-val.success { color: var(--success); }

  .bio-head {
    font-family: var(--display);
    font-weight: 600;
    font-size: 1.2rem;
    color: var(--ink);
    margin: 0 0 1rem;
  }

  .bio {
    color: var(--ink-muted);
    font-size: 1.02rem;
    line-height: 1.65;
  }
  .bio p { margin: 0 0 1.1rem; white-space: pre-line; }
  .bio .empty { color: var(--ink-faint); font-style: italic; }

  .source-line { margin: 1.8rem 0 0; font-size: 0.8rem; color: var(--ink-faint); }
  .source-line a { color: var(--ink-muted); text-decoration: underline; }
  .source-line a:hover { color: var(--accent); }

  @media (max-width: 1000px) {
    .profile {
      grid-template-columns: 1fr;
      gap: 2rem;
    }
    .card { position: static; }
  }
  @media (max-width: 600px) {
    .profile { padding: 0 1.25rem; }
  }
</style>
