<script lang="ts">
  interface Doctor {
    slug: string;
    fullNameKa: string;
    fullNameEn: string;
    photoUrl: string | null;
    isAcceptingNewPatients: boolean;
    treatsChildren: boolean;
    treatsAdults: boolean;
  }

  let { doctor }: { doctor: Doctor } = $props();

  const initial = doctor.fullNameEn.charAt(0).toUpperCase();
  const hue = doctor.slug.split('').reduce((h, c) => h + c.charCodeAt(0), 0) % 360;
</script>

<article class="card">
  {#if doctor.photoUrl}
    <img class="photo" src={doctor.photoUrl} alt="" />
  {:else}
    <div class="photo placeholder" style="background: hsl({hue}, 50%, 70%)">
      {initial}
    </div>
  {/if}
  <div class="body">
    <div class="name-en">{doctor.fullNameEn}</div>
    <div class="name-ka">{doctor.fullNameKa}</div>
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
  </div>
</article>

<style>
  .card {
    display: flex;
    gap: 1rem;
    padding: 1rem;
    border: 1px solid #ddd;
    border-radius: 8px;
  }
  .photo {
    width: 72px;
    height: 72px;
    border-radius: 50%;
    object-fit: cover;
    flex-shrink: 0;
  }
  .photo.placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.75rem;
    font-weight: 600;
    color: #fff;
  }
  .name-en { font-weight: 600; }
  .name-ka { color: #555; font-size: 0.9rem; }
  .badges {
    list-style: none;
    padding: 0;
    margin: 0.5rem 0 0 0;
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  .badge {
    font-size: 0.85rem;
    padding: 0.15rem 0.5rem;
    background: #f0f0f0;
    border-radius: 4px;
  }
  .badge.accepting {
    background: #d4f5d4;
  }
</style>
