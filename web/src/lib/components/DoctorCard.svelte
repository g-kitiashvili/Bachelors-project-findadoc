<script lang="ts">
  interface SpecialtyRef { slug: string; nameKa: string; nameEn: string; }

  interface Doctor {
    slug: string;
    fullNameKa: string;
    fullNameEn: string;
    photoUrl: string | null;
    isAcceptingNewPatients: boolean;
    treatsChildren: boolean;
    treatsAdults: boolean;
    specialtyKa: string | null;
    specialtyEn: string | null;
    primarySpecialty: SpecialtyRef | null;
    primaryClinic: { slug: string; nameKa: string; nameEn: string; address: string | null } | null;
  }

  let { doctor }: { doctor: Doctor } = $props();

  const initial = doctor.fullNameEn.trim().charAt(0).toUpperCase() || "·";
  const bgClass = (() => {
    const sum = doctor.slug.split("").reduce((s, c) => s + c.charCodeAt(0), 0);
    const buckets = ["bg-a", "bg-b", "bg-c", "bg-d", "bg-e", "bg-f"] as const;
    return buckets[sum % buckets.length];
  })();
  const sourceHost = null as string | null;
</script>

<div class="card">
  <a class="card-link" href="/doctors/{doctor.slug}">
    <div class="photo {bgClass}">
      {#if doctor.photoUrl}
        <img src={doctor.photoUrl} alt="" />
      {:else}
        <span class="initial">{initial}</span>
      {/if}
      {#if doctor.isAcceptingNewPatients}
        <span class="tag-accepting"><span class="dot"></span>Accepting</span>
      {/if}
      {#if sourceHost}
        <span class="tag-source">{sourceHost}</span>
      {/if}
    </div>
  </a>
  <div class="info">
    <a class="name-link" href="/doctors/{doctor.slug}">
      <h3 class="name">{doctor.fullNameEn}</h3>
    </a>
    {#if doctor.primarySpecialty}
      <a class="specialty-pill" href={`/specialties/${doctor.primarySpecialty.slug}`}>
        {doctor.primarySpecialty.nameEn}
      </a>
    {:else if doctor.specialtyEn}
      <span class="specialty-pill specialty-pill--raw">{doctor.specialtyEn}</span>
    {/if}
    {#if doctor.primaryClinic}
      <a class="clinic-pill" href={`/clinics/${doctor.primaryClinic.slug}`}>{doctor.primaryClinic.nameEn}</a>
    {/if}
    <div class="meta">
      {#if doctor.treatsAdults}
        <span class="pill">Adults</span>
      {/if}
      {#if doctor.treatsChildren}
        <span class="pill">Children</span>
      {/if}
    </div>
  </div>
</div>

<style>
  .card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 14px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    transition: border-color 0.15s, transform 0.15s, box-shadow 0.15s;
    color: inherit;
  }
  .card:hover {
    border-color: var(--line-strong);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px -12px rgba(14, 19, 32, 0.16);
  }
  .card-link {
    display: block;
    color: inherit;
    text-decoration: none;
  }
  .name-link {
    color: inherit;
    text-decoration: none;
    display: block;
  }

  .photo {
    aspect-ratio: 1 / 1;
    background: var(--bg-soft);
    position: relative;
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
    font-size: 4.5rem;
    color: var(--ink);
    opacity: 0.75;
    letter-spacing: -0.02em;
  }
  .bg-a { background: linear-gradient(135deg, #f6ebe8, #e8c9c0); }
  .bg-b { background: linear-gradient(135deg, #e5ebf5, #c6d2e6); }
  .bg-c { background: linear-gradient(135deg, #f2ebd7, #d9c895); }
  .bg-d { background: linear-gradient(135deg, #e5f0e8, #bfdbc4); }
  .bg-e { background: linear-gradient(135deg, #f2e7f0, #d5b5cc); }
  .bg-f { background: linear-gradient(135deg, #ecedea, #c8c0be); }

  .tag-accepting {
    position: absolute;
    top: 0.85rem;
    left: 0.85rem;
    background: white;
    color: var(--ink);
    font-size: 0.74rem;
    font-weight: 600;
    padding: 0.3rem 0.6rem;
    border-radius: 6px;
    box-shadow: 0 2px 6px rgba(14, 19, 32, 0.08);
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
  }
  .tag-accepting .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--success);
  }
  .tag-source {
    position: absolute;
    bottom: 0.7rem;
    right: 0.85rem;
    font-size: 0.7rem;
    color: var(--ink-muted);
    background: rgba(255, 255, 255, 0.92);
    padding: 0.25rem 0.55rem;
    border-radius: 4px;
    font-weight: 500;
  }

  .info {
    padding: 1.2rem 1.3rem 1.4rem;
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  .name {
    font-family: var(--display);
    font-weight: 600;
    font-size: 1.25rem;
    line-height: 1.15;
    color: var(--ink);
    margin: 0 0 0.25rem;
    letter-spacing: -0.015em;
  }
  .specialty-pill {
    display: inline-block;
    margin-top: 0.6rem;
    margin-bottom: 0.75rem;
    background: var(--bg-soft);
    border: 1px solid var(--line);
    border-radius: 100px;
    padding: 0.25rem 0.75rem;
    font-size: 0.78rem;
    color: var(--ink);
    font-weight: 500;
    transition: background 0.15s, color 0.15s, border-color 0.15s;
    text-decoration: none;
    align-self: flex-start;
  }
  .specialty-pill:hover {
    background: var(--accent);
    border-color: var(--accent);
    color: white;
  }
  .specialty-pill--raw {
    color: var(--ink-muted);
    cursor: default;
  }
  .specialty-pill--raw:hover {
    background: var(--bg-soft);
    border-color: var(--line);
    color: var(--ink-muted);
  }
  .clinic-pill {
    display: inline-block;
    margin-bottom: 0.75rem;
    background: transparent;
    border: 1px dashed var(--line-strong);
    border-radius: 100px;
    padding: 0.25rem 0.75rem;
    font-size: 0.76rem;
    color: var(--ink-muted);
    font-weight: 500;
    transition: background 0.15s, color 0.15s, border-color 0.15s;
    text-decoration: none;
    align-self: flex-start;
  }
  .clinic-pill:hover {
    background: var(--bg-soft);
    border-color: var(--ink-muted);
    color: var(--ink);
  }
  .meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin-top: auto;
  }
  .pill {
    border: 1px solid var(--line);
    background: var(--bg-soft);
    color: var(--ink-muted);
    font-size: 0.76rem;
    font-weight: 500;
    padding: 0.25rem 0.6rem;
    border-radius: 6px;
  }
</style>
