<footer class="footer">
  <div class="footer-inner">
    <div>
      <div class="footer-brand">findadoc<span class="footer-brand-dot">.</span></div>
      <p class="footer-desc">
        An open, bilingual medical directory for Georgia. A bachelor's thesis project
        building on the NYU Langone Find-a-Doctor reference, localized for the
        Georgian market.
      </p>
    </div>
    <div class="footer-col">
      <h4>Browse</h4>
      <ul>
        <li><a href="/doctors">All doctors</a></li>
        <li><a href="/specialties">By specialty</a></li>
        <li><a href="/conditions">By condition</a></li>
        <li><span class="soon" title="Coming soon">By clinic</span></li>
      </ul>
    </div>
    <div class="footer-col">
      <h4>Project</h4>
      <ul>
        <li><a href="/about">About</a></li>
        <li><a href="/sources">Data sources</a></li>
        <li><a href="/thesis">Thesis</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <span>© 2026 findadoc · Free University of Tbilisi</span>
    <span>Data scraped from public sources · Updated daily</span>
  </div>
</footer>

<style>
  .footer {
    background: var(--ink);
    color: rgba(255, 255, 255, 0.75);
    padding: 4rem 0 2.5rem;
    margin-top: 6rem;
  }
  .footer-inner {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 2rem;
    display: grid;
    grid-template-columns: 1.5fr 1fr 1fr;
    gap: 3rem;
  }
  .footer-brand {
    font-family: var(--display);
    font-weight: 600;
    font-size: 1.8rem;
    color: white;
    letter-spacing: -0.02em;
    margin-bottom: 0.8rem;
  }
  .footer-brand-dot {
    color: var(--accent-soft);
  }
  .footer-desc {
    font-size: 0.92rem;
    line-height: 1.55;
    max-width: 360px;
    margin: 0;
  }
  .footer-col h4 {
    color: white;
    font-size: 0.86rem;
    font-weight: 600;
    margin: 0 0 1rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }
  .footer-col ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
  }
  .footer-col a {
    color: rgba(255, 255, 255, 0.65);
    font-size: 0.92rem;
    transition: color 0.15s;
  }
  .footer-col a:hover {
    color: white;
  }
  .footer-col .soon {
    color: rgba(255, 255, 255, 0.35);
    font-size: 0.92rem;
    cursor: not-allowed;
  }
  .footer-bottom {
    max-width: 1280px;
    margin: 3rem auto 0;
    padding: 1.5rem 2rem 0;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    justify-content: space-between;
    font-size: 0.82rem;
    color: rgba(255, 255, 255, 0.5);
  }

  @media (max-width: 1000px) {
    .footer-inner {
      grid-template-columns: 1fr 1fr;
    }
  }
  @media (max-width: 600px) {
    .footer-inner {
      grid-template-columns: 1fr;
      padding: 0 1.25rem;
    }
    .footer-bottom {
      padding: 1.5rem 1.25rem 0;
      flex-direction: column;
      gap: 0.5rem;
    }
  }
</style>
