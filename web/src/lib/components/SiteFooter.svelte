<script lang="ts">
  import * as m from "$lib/paraglide/messages";
  import { href } from "$lib/i18n";
</script>

<footer class="footer">
  <div class="footer-inner">
    <div>
      <div class="footer-brand">findadoc<span class="footer-brand-dot">.</span></div>
      <p class="footer-desc">{m.footer_tagline()}</p>
    </div>
    <div class="footer-col">
      <h4>{m.footer_browse()}</h4>
      <ul>
        <li><a href={href('/doctors')}>{m.footer_all_doctors()}</a></li>
        <li><a href={href('/specialties')}>{m.footer_by_specialty()}</a></li>
        <li><a href={href('/conditions')}>{m.footer_by_condition()}</a></li>
        <li><a href={href('/clinics')}>{m.footer_by_clinic()}</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h4>{m.footer_legal()}</h4>
      <ul>
        <li><a href={href('/privacy')}>{m.footer_privacy()}</a></li>
        <li><a href={href('/terms')}>{m.footer_terms()}</a></li>
        <li><a href={href('/takedown')}>{m.footer_takedown()}</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <span>{m.footer_copyright()}</span>
    <span>{m.footer_data_note()}</span>
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
