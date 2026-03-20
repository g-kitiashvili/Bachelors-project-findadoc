<script lang="ts">
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
  }

  let { doctor }: { doctor: Doctor } = $props();
  let activeTab = $state<"en" | "ka">("en");

  const initial = doctor.fullNameEn.charAt(0).toUpperCase();
  const hue = doctor.slug.split('').reduce((h, c) => h + c.charCodeAt(0), 0) % 360;
  const activeBio = $derived(activeTab === "en" ? doctor.bioEn : doctor.bioKa);
</script>

<article class="profile">
  <header class="hero">
    {#if doctor.photoUrl}
      <img class="photo" src={doctor.photoUrl} alt="" />
    {:else}
      <div class="photo placeholder" style="background: hsl({hue}, 50%, 70%)">
        {initial}
      </div>
    {/if}
    <div class="names">
      <div class="name-en">{doctor.fullNameEn}</div>
      <div class="name-ka">{doctor.fullNameKa}</div>
      {#if doctor.specialtyEn || doctor.specialtyKa}
        <div class="specialty">{doctor.specialtyEn ?? doctor.specialtyKa}</div>
      {/if}
      {#if doctor.gender}
        <div class="meta">{doctor.gender}</div>
      {/if}
    </div>
  </header>

  <ul class="badges">
    {#if doctor.isAcceptingNewPatients}
      <li class="badge accepting">✓ Accepting new patients</li>
    {/if}
    {#if doctor.treatsChildren}
      <li class="badge">👶 Children</li>
    {/if}
    {#if doctor.treatsAdults}
      <li class="badge">🧓 Adults</li>
    {/if}
  </ul>

  <div class="tabs" role="tablist">
    <button
      role="tab"
      aria-selected={activeTab === "en"}
      class:active={activeTab === "en"}
      onclick={() => (activeTab = "en")}>
      English
    </button>
    <button
      role="tab"
      aria-selected={activeTab === "ka"}
      class:active={activeTab === "ka"}
      onclick={() => (activeTab = "ka")}>
      ქართული
    </button>
  </div>

  <div class="bio" role="tabpanel">
    {#if activeBio}
      <p>{activeBio}</p>
    {:else}
      <p class="empty">No bio available.</p>
    {/if}
  </div>
</article>

<style>
  .profile {
    max-width: 720px;
    margin: 0 auto;
    padding: 0 1rem 3rem;
    font-family: system-ui, sans-serif;
  }
  .hero {
    display: flex;
    gap: 1.5rem;
    align-items: center;
    margin-bottom: 1.5rem;
  }
  .photo {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    object-fit: cover;
    flex-shrink: 0;
  }
  .photo.placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 3rem;
    font-weight: 600;
  }
  .name-en { font-size: 1.5rem; font-weight: 700; }
  .name-ka { color: #555; font-size: 1.1rem; }
  .meta { color: #888; font-size: 0.9rem; text-transform: capitalize; }
  .badges {
    list-style: none;
    padding: 0;
    margin: 0 0 2rem 0;
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  .badge {
    font-size: 0.9rem;
    padding: 0.25rem 0.6rem;
    background: #f0f0f0;
    border-radius: 4px;
  }
  .badge.accepting { background: #d4f5d4; }
  .specialty {
    color: #2563eb;
    font-size: 1rem;
    font-weight: 500;
    margin-top: 0.25rem;
  }
  .tabs {
    display: flex;
    gap: 0;
    border-bottom: 1px solid #ddd;
    margin-bottom: 1rem;
  }
  .tabs button {
    background: transparent;
    border: none;
    padding: 0.6rem 1.2rem;
    cursor: pointer;
    font-size: 1rem;
    color: #555;
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
  }
  .tabs button.active {
    color: #2563eb;
    border-bottom-color: #2563eb;
    font-weight: 600;
  }
  .bio p { line-height: 1.6; }
  .bio .empty { color: #999; font-style: italic; }
</style>
