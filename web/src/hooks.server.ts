import type { Handle } from '@sveltejs/kit';
import { redirect } from '@sveltejs/kit';
import { paraglideMiddleware } from '$lib/paraglide/server';

export const handle: Handle = ({ event, resolve }) => {
  if (event.url.pathname === '/') {
    const cookieLocale = event.cookies.get('PARAGLIDE_LOCALE');
    throw redirect(307, `/${cookieLocale === 'en' ? 'en' : 'ka'}`);
  }
  return paraglideMiddleware(event.request, ({ request, locale }) => {
    event.request = request;
    return resolve(event, {
      transformPageChunk: ({ html }) => html.replace('%lang%', locale)
    });
  });
};
