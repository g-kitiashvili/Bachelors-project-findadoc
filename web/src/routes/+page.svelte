<script lang="ts">
  import SearchBar from "$lib/components/SearchBar.svelte";

  let { data } = $props();

  // Three sample doctors (whatever the API returns) used for the hero collage initials.
  const slot1 = $derived(data.sample[0]);
  const slot2 = $derived(data.sample[1]);
  const slot3 = $derived(data.sample[2]);

  function initial(d?: { fullNameEn?: string | null }): string {
    if (!d || !d.fullNameEn) return "·";
    return d.fullNameEn.trim().charAt(0).toUpperCase();
  }

  const total = $derived(data.total ?? 0);
</script>

<svelte:head>
  <title>Find-a-Doc — bilingual medical directory for Georgia</title>
</svelte:head>

<section class="hero">
  <div class="hero-inner">
    <div class="hero-text">
      <span class="hero-eyebrow">Georgia's open medical directory</span>
      <h1 class="hero-title">
        Find a doctor<br />
        <span class="hero-title-accent">you can trust.</span>
      </h1>
      <p class="hero-sub">
        Search {total > 0 ? `${total}+ ` : ""}verified Georgian doctors across
        specialties, clinics, and conditions — in Georgian and English.
      </p>

      <SearchBar autofocus={false} />

      <div class="chips">
        <span class="chips-label">Try</span>
        <a class="chip" href="/doctors?q=Cardiologist">Cardiologist</a>
        <a class="chip chip-ge" href="/doctors?q=გასტროენტეროლოგი">გასტროენტეროლოგი</a>
        <a class="chip" href="/doctors?q=Pediatrician">Pediatrician</a>
        <a class="chip chip-ge" href="/doctors?q=ნეიროლოგი">ნეიროლოგი</a>
      </div>
    </div>

    <div class="hero-collage" aria-hidden="true">
      <div class="hero-photo hero-photo-1">{initial(slot1)}</div>
      <div class="hero-photo hero-photo-2">{initial(slot2)}</div>
      <div class="hero-photo hero-photo-3">{initial(slot3)}</div>
      <div class="hero-badge">
        <div class="hero-badge-num">{total}+</div>
        <div class="hero-badge-text">verified<br />profiles</div>
      </div>
    </div>
  </div>
</section>

<section class="stats">
  <div class="stats-inner">
    <div>
      <div class="stat-num">{total}<span class="stat-num-accent">+</span></div>
      <div class="stat-label">Doctors indexed</div>
    </div>
    <div>
      <div class="stat-num">16</div>
      <div class="stat-label">Specialties</div>
    </div>
    <div>
      <div class="stat-num">2</div>
      <div class="stat-label">Sources (and growing)</div>
    </div>
    <div>
      <div class="stat-num">EN<span class="stat-num-accent">·</span>KA</div>
      <div class="stat-label">Bilingual</div>
    </div>
  </div>
</section>

<style>
  .hero {
    border-bottom: 1px solid var(--line);
    padding: 6rem 0 5rem;
  }
  .hero-inner {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 2rem;
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 4rem;
    align-items: center;
  }
  .hero-text {
    min-width: 0;
  }
  .hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--accent);
    background: var(--accent-soft);
    padding: 0.4rem 0.9rem;
    border-radius: 999px;
    margin-bottom: 1.6rem;
  }
  .hero-eyebrow::before {
    content: "";
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--accent);
  }
  .hero-title {
    font-family: var(--display);
    font-weight: 600;
    font-size: clamp(2.4rem, 4.8vw, 4.2rem);
    line-height: 1.02;
    letter-spacing: -0.025em;
    color: var(--ink);
    margin: 0 0 1.5rem;
  }
  .hero-title-accent {
    color: var(--accent);
  }
  .hero-sub {
    font-size: 1.08rem;
    color: var(--ink-muted);
    line-height: 1.55;
    max-width: 520px;
    margin: 0 0 2.2rem;
  }

  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1.5rem;
    align-items: center;
  }
  .chips-label {
    font-size: 0.82rem;
    color: var(--ink-faint);
    font-weight: 500;
    margin-right: 0.4rem;
  }
  .chip {
    border: 1px solid var(--line);
    background: var(--surface);
    color: var(--ink-muted);
    font-size: 0.86rem;
    font-weight: 500;
    padding: 0.45rem 0.95rem;
    border-radius: 999px;
    transition: all 0.15s;
  }
  .chip:hover {
    border-color: var(--accent);
    color: var(--accent);
    background: var(--accent-soft);
  }
  .chip-ge {
    font-family: var(--sans-ge);
  }

  /* hero collage on the right */
  .hero-collage {
    position: relative;
    aspect-ratio: 5 / 6;
    max-width: 460px;
    margin-left: auto;
    width: 100%;
  }
  .hero-photo {
    position: absolute;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 10px 30px -10px rgba(14, 19, 32, 0.18);
    background: var(--bg-soft);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: var(--display);
    color: var(--accent);
    font-weight: 500;
  }
  .hero-photo-1 {
    width: 60%;
    aspect-ratio: 4/5;
    top: 0;
    left: 0;
    background: linear-gradient(140deg, #fde3dc, #fbc8bd);
    font-size: 4rem;
  }
  .hero-photo-2 {
    width: 50%;
    aspect-ratio: 1/1;
    bottom: 12%;
    right: 0;
    background: linear-gradient(140deg, #e2e7f2, #c5cfe6);
    color: var(--ink);
    font-size: 3.2rem;
  }
  .hero-photo-3 {
    width: 38%;
    aspect-ratio: 1/1;
    top: 56%;
    left: 8%;
    background: linear-gradient(140deg, #f2ead9, #e2d2a8);
    color: var(--ink);
    font-size: 2.6rem;
  }
  .hero-badge {
    position: absolute;
    top: 10%;
    right: -2%;
    background: white;
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    box-shadow: 0 6px 20px -6px rgba(14, 19, 32, 0.12);
    display: flex;
    align-items: center;
    gap: 0.7rem;
    font-size: 0.84rem;
  }
  .hero-badge-num {
    font-family: var(--display);
    font-weight: 600;
    font-size: 1.4rem;
    color: var(--accent);
    line-height: 1;
  }
  .hero-badge-text {
    color: var(--ink-muted);
    line-height: 1.2;
    font-size: 0.82rem;
  }

  /* stats strip */
  .stats {
    background: var(--bg-soft);
    border-bottom: 1px solid var(--line);
  }
  .stats-inner {
    max-width: 1280px;
    margin: 0 auto;
    padding: 2.5rem 2rem;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 2.5rem;
  }
  .stat-num {
    font-family: var(--display);
    font-weight: 600;
    font-size: 2.5rem;
    line-height: 1;
    color: var(--ink);
    letter-spacing: -0.02em;
  }
  .stat-num-accent {
    color: var(--accent);
  }
  .stat-label {
    margin-top: 0.5rem;
    font-size: 0.86rem;
    color: var(--ink-muted);
    font-weight: 500;
  }

  @media (max-width: 1000px) {
    .hero {
      padding: 4rem 0 3rem;
    }
    .hero-inner {
      grid-template-columns: 1fr;
      gap: 3rem;
    }
    .hero-collage {
      display: none;
    }
    .stats-inner {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  @media (max-width: 600px) {
    .hero-inner {
      padding: 0 1.25rem;
    }
    .stats-inner {
      grid-template-columns: 1fr 1fr;
      gap: 1.5rem;
      padding: 2rem 1.25rem;
    }
  }
</style>
