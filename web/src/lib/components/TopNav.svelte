<script lang="ts">
  let { active = "doctors" }: { active?: "doctors" | "specialties" | "conditions" | "clinics" | "about" } = $props();
</script>

<nav class="nav">
  <div class="nav-inner">
    <a href="/" class="brand">findadoc<span class="brand-dot">.</span></a>
    <div class="nav-links">
      <a href="/doctors" class:active={active === "doctors"}>Find a Doctor</a>
      <a href="/specialties" class:active={active === "specialties"}>Specialties</a>
      <a href="/conditions" class:disabled={true}>Conditions</a>
      <a href="/clinics" class:disabled={true}>Clinics</a>
      <a href="/about" class:disabled={true}>About</a>
    </div>
    <div class="nav-right">
      <span class="nav-lang"><strong>EN</strong> / ქართული</span>
      <button class="nav-cta" type="button" disabled aria-disabled="true">Request callback</button>
    </div>
  </div>
</nav>

<style>
  .nav {
    position: sticky;
    top: 0;
    z-index: 50;
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--line);
  }
  .nav-inner {
    max-width: 1280px;
    margin: 0 auto;
    padding: 1rem 2rem;
    display: flex;
    align-items: center;
    gap: 2.5rem;
  }
  .brand {
    font-family: var(--display);
    font-weight: 600;
    font-size: 1.3rem;
    letter-spacing: -0.02em;
    color: var(--ink);
  }
  .brand-dot {
    color: var(--accent);
  }
  .nav-links {
    display: flex;
    gap: 2rem;
    font-size: 0.92rem;
    font-weight: 500;
    color: var(--ink-muted);
  }
  .nav-links a {
    position: relative;
    padding: 0.3rem 0;
    transition: color 0.15s ease;
  }
  .nav-links a:hover {
    color: var(--ink);
  }
  .nav-links a.disabled {
    color: var(--ink-faint);
    cursor: not-allowed;
    pointer-events: none;
  }
  .nav-links a.active {
    color: var(--accent);
  }
  .nav-links a.active::after {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    bottom: -1.05rem;
    height: 2px;
    background: var(--accent);
  }
  .nav-right {
    margin-left: auto;
    display: flex;
    gap: 1rem;
    align-items: center;
  }
  .nav-lang {
    font-size: 0.82rem;
    color: var(--ink-faint);
    font-weight: 500;
    padding-right: 1rem;
    border-right: 1px solid var(--line);
  }
  .nav-lang strong {
    color: var(--ink);
  }
  .nav-cta {
    background: var(--ink);
    color: white;
    border: none;
    padding: 0.6rem 1.1rem;
    border-radius: 6px;
    font-size: 0.88rem;
    font-weight: 500;
    transition: background 0.15s;
  }
  .nav-cta:not(:disabled):hover {
    background: var(--accent);
  }
  .nav-cta:disabled {
    opacity: 0.55;
    cursor: not-allowed;
  }

  @media (max-width: 900px) {
    .nav-inner {
      padding: 1rem 1.25rem;
      gap: 1.25rem;
    }
    .nav-links {
      display: none;
    }
  }
</style>
