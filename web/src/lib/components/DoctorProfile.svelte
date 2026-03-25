<script lang="ts">
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
  }

  let { doctor }: { doctor: Doctor } = $props();
  let activeTab = $state<"en" | "ka">("en");

  const initial = doctor.fullNameEn.trim().charAt(0).toUpperCase() || "·";
  const activeBio = $derived(activeTab === "en" ? doctor.bioEn : doctor.bioKa);

  // Deterministic photo gradient based on slug (matches DoctorCard logic)
  const bgClass = (() => {
    const sum = doctor.slug.split("").reduce((s, c) => s + c.charCodeAt(0), 0);
    const buckets = ["bg-a", "bg-b", "bg-c", "bg-d", "bg-e", "bg-f"] as const;
    return buckets[sum % buckets.length];
  })();

  const treatsLabel = (() => {
    const parts: string[] = [];
    if (doctor.treatsAdults) parts.push("Adults");
    if (doctor.treatsChildren) parts.push("Children");
    return parts.length ? parts.join(" · ") : "—";
  })();
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
        <span class="meta-label">Treats</span>
        <span class="meta-val">{treatsLabel}</span>
      </div>
      {#if doctor.gender}
        <div class="meta-row">
          <span class="meta-label">Gender</span>
          <span class="meta-val">{doctor.gender}</span>
        </div>
      {/if}
      <div class="meta-row">
        <span class="meta-label">Accepting</span>
        <span class="meta-val" class:success={doctor.isAcceptingNewPatients}>
          {doctor.isAcceptingNewPatients ? "Yes" : "No"}
        </span>
      </div>
      <button class="cta-btn" type="button" disabled aria-disabled="true">
        Request callback
      </button>
    </div>
  </aside>

  <div class="body">
    <div class="eyebrow">Doctor profile</div>
    <h1 class="name">{doctor.fullNameEn}</h1>
    <p class="name-ka">{doctor.fullNameKa}</p>

    {#if doctor.specialties && doctor.specialties.length > 0}
      <div class="specialty-row">
        {#each doctor.specialties as s (s.slug)}
          <a class="profile-specialty-pill" href={`/specialties/${s.slug}`} class:primary={s.isPrimary}>
            {s.nameEn}
            {#if s.isPrimary}<span class="primary-dot" title="Primary">●</span>{/if}
          </a>
        {/each}
      </div>
    {:else if doctor.specialtyEn}
      <div class="specialty-row">
        <span class="profile-specialty-pill profile-specialty-pill--raw">{doctor.specialtyEn}</span>
      </div>
    {/if}

    <div class="quick-meta">
      <div class="quick">
        <span class="quick-label">Treats</span>
        <span class="quick-val">{treatsLabel}</span>
      </div>
      <div class="quick">
        <span class="quick-label">Accepting</span>
        <span class="quick-val" class:success={doctor.isAcceptingNewPatients}>
          {doctor.isAcceptingNewPatients ? "Yes" : "No"}
        </span>
      </div>
    </div>

    <div class="tabs" role="tablist">
      <button
        role="tab"
        type="button"
        aria-selected={activeTab === "en"}
        class="tab"
        class:active={activeTab === "en"}
        onclick={() => (activeTab = "en")}>
        English
      </button>
      <button
        role="tab"
        type="button"
        aria-selected={activeTab === "ka"}
        class="tab"
        class:active={activeTab === "ka"}
        onclick={() => (activeTab = "ka")}>
        ქართული
      </button>
    </div>

    <div class="bio" role="tabpanel">
      {#if activeBio}
        <p>{activeBio}</p>
      {:else}
        <p class="empty">No biography available in this language yet.</p>
      {/if}
    </div>
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
    aspect-ratio: 4 / 3.5;
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

  .cta-btn {
    background: var(--accent);
    color: white;
    border: none;
    padding: 0.95rem 1.4rem;
    border-radius: 10px;
    font-size: 0.95rem;
    font-weight: 600;
    margin-top: 0.5rem;
    transition: background 0.15s;
  }
  .cta-btn:not(:disabled):hover { background: var(--accent-deep); }
  .cta-btn:disabled { opacity: 0.55; cursor: not-allowed; }

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
  .name-ka {
    font-family: var(--sans-ge);
    font-size: 1.4rem;
    color: var(--ink-muted);
    margin: 0 0 1.8rem;
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

  .tabs {
    display: flex;
    gap: 0;
    border-bottom: 1px solid var(--line);
    margin-bottom: 2rem;
  }
  .tab {
    background: transparent;
    border: none;
    padding: 0.9rem 0;
    margin-right: 2.4rem;
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--ink-faint);
    position: relative;
    cursor: pointer;
    transition: color 0.15s;
  }
  .tab:hover { color: var(--ink-muted); }
  .tab.active { color: var(--ink); font-weight: 600; }
  .tab.active::after {
    content: "";
    position: absolute;
    bottom: -1px;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--accent);
  }

  .bio {
    color: var(--ink-muted);
    font-size: 1.02rem;
    line-height: 1.65;
  }
  .bio p { margin: 0 0 1.1rem; white-space: pre-line; }
  .bio .empty { color: var(--ink-faint); font-style: italic; }

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
