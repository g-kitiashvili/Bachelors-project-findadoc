<script lang="ts">
  interface SpecialtyRef { slug: string; nameEn: string }
  interface Doc {
    slug: string;
    fullNameEn: string;
    photoUrl: string | null;
    primarySpecialty: SpecialtyRef | null;
    specialtyEn: string | null;
  }

  let { doctors }: { doctors: Doc[] } = $props();

  let rail: HTMLDivElement;
  function page(dir: number) {
    if (!rail) return;
    rail.scrollBy({ left: dir * rail.clientWidth * 0.85, behavior: "smooth" });
  }

  const initial = (d: Doc) => d.fullNameEn.trim().charAt(0).toUpperCase() || "·";
  const bg = (slug: string) => {
    const sum = slug.split("").reduce((s, c) => s + c.charCodeAt(0), 0);
    return ["bg-a", "bg-b", "bg-c", "bg-d", "bg-e", "bg-f"][sum % 6];
  };
</script>

{#if doctors.length > 0}
  <section class="similar">
    <div class="head">
      <h2>Similar doctors</h2>
      {#if doctors.length > 5}
        <div class="nav">
          <button type="button" aria-label="Previous" onclick={() => page(-1)}>‹</button>
          <button type="button" aria-label="Next" onclick={() => page(1)}>›</button>
        </div>
      {/if}
    </div>
    <div class="rail" bind:this={rail}>
      {#each doctors as d (d.slug)}
        <a class="mini" href="/doctors/{d.slug}">
          <div class="avatar {bg(d.slug)}">
            {#if d.photoUrl}<img src={d.photoUrl} alt="" />{:else}<span>{initial(d)}</span>{/if}
          </div>
          <div class="name">{d.fullNameEn}</div>
          <div class="spec">{d.primarySpecialty?.nameEn ?? d.specialtyEn ?? ""}</div>
        </a>
      {/each}
    </div>
  </section>
{/if}

<style>
  .similar { max-width: 1280px; margin: 3rem auto; padding: 0 2rem; }
  .head { display: flex; align-items: center; justify-content: space-between; gap: 1rem; margin-bottom: 1.1rem; }
  .head h2 { font-family: var(--display); font-size: 1.4rem; letter-spacing: -0.02em; margin: 0; }
  .nav { display: flex; gap: 0.4rem; flex-shrink: 0; }
  .nav button {
    width: 2.1rem; height: 2.1rem; border-radius: 50%;
    border: 1px solid var(--line-strong); background: var(--surface);
    color: var(--ink); font-size: 1.15rem; line-height: 1; cursor: pointer;
    display: inline-flex; align-items: center; justify-content: center;
    transition: border-color 0.15s, color 0.15s, background 0.15s;
  }
  .nav button:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-soft); }

  .rail {
    display: flex; gap: 1rem; overflow-x: auto; scroll-snap-type: x proximity;
    padding-bottom: 0.5rem; scrollbar-width: thin;
  }
  .mini {
    flex: 0 0 calc((100% - 4rem) / 5); /* ~5 cards visible (4 × 1rem gaps) */
    min-width: 150px;
    scroll-snap-align: start;
    background: var(--surface); border: 1px solid var(--line); border-radius: 12px;
    padding: 1.1rem 1rem; text-decoration: none; color: inherit;
    display: flex; flex-direction: column; align-items: center; text-align: center;
    transition: border-color 0.15s, transform 0.15s, box-shadow 0.15s;
  }
  .mini:hover { border-color: var(--line-strong); transform: translateY(-2px); box-shadow: 0 8px 20px -12px rgba(14, 19, 32, 0.16); }
  .avatar {
    width: 64px; height: 64px; border-radius: 50%; overflow: hidden;
    display: flex; align-items: center; justify-content: center; margin-bottom: 0.7rem;
    font-family: var(--display); font-weight: 500; font-size: 1.6rem; color: var(--ink);
  }
  .avatar img { width: 100%; height: 100%; object-fit: cover; object-position: center 25%; }
  .name { font-weight: 600; font-size: 0.92rem; line-height: 1.2; color: var(--ink); margin-bottom: 0.3rem; }
  .spec { font-size: 0.78rem; color: var(--ink-muted); line-height: 1.25; }
  .bg-a { background: linear-gradient(135deg, #f6ebe8, #e8c9c0); }
  .bg-b { background: linear-gradient(135deg, #e5ebf5, #c6d2e6); }
  .bg-c { background: linear-gradient(135deg, #f2ebd7, #d9c895); }
  .bg-d { background: linear-gradient(135deg, #e5f0e8, #bfdbc4); }
  .bg-e { background: linear-gradient(135deg, #f2e7f0, #d5b5cc); }
  .bg-f { background: linear-gradient(135deg, #ecedea, #c8c0be); }

  @media (max-width: 900px) {
    .mini { flex: 0 0 calc((100% - 2rem) / 3); } /* 3 per row */
    .similar { padding: 0 1.25rem; }
  }
  @media (max-width: 560px) {
    .mini { flex: 0 0 68%; } /* peek the next card */
  }
</style>
