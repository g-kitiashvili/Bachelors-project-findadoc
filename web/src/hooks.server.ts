import type { Handle } from '@sveltejs/kit';
import { redirect } from '@sveltejs/kit';
import { paraglideMiddleware } from '$lib/paraglide/server';

// 'unsafe-inline' on script/style is a deliberate relaxation: SvelteKit's hydration
// bootstrap and Svelte's scoped/inline styles are inline, and we don't run a nonce setup.
// 'wasm-unsafe-eval' lets the body-map's Three.js DRACO decoder compile its WebAssembly.
// Font CSS comes from Fontshare + Google Fonts; map tiles and doctor photos are remote.
const CSP = [
  "default-src 'self'",
  "script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval'",
  // The body-map's Three.js DRACO decoder runs in a worker created from a blob: URL.
  "worker-src 'self' blob:",
  "style-src 'self' 'unsafe-inline' https://api.fontshare.com https://fonts.googleapis.com",
  // Fontshare serves its CSS from api.fontshare.com but the font files from cdn.fontshare.com.
  "font-src 'self' data: https://cdn.fontshare.com https://fonts.gstatic.com",
  "img-src 'self' data: https:",
  "connect-src 'self' https://*.tile.openstreetmap.org",
  "object-src 'none'",
  "base-uri 'self'",
  "frame-ancestors 'none'"
].join('; ');

const SECURITY_HEADERS: Record<string, string> = {
  'Content-Security-Policy': CSP,
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=(self)',
  'X-Frame-Options': 'DENY'
};

export const handle: Handle = ({ event, resolve }) => {
  if (event.url.pathname === '/') {
    const cookieLocale = event.cookies.get('PARAGLIDE_LOCALE');
    throw redirect(307, `/${cookieLocale === 'en' ? 'en' : 'ka'}`);
  }
  return paraglideMiddleware(event.request, async ({ request, locale }) => {
    event.request = request;
    const response = await resolve(event, {
      transformPageChunk: ({ html }) => html.replace('%lang%', locale)
    });
    for (const [key, value] of Object.entries(SECURITY_HEADERS)) {
      response.headers.set(key, value);
    }
    return response;
  });
};
