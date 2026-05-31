export { localizeHref as href } from '$lib/paraglide/runtime';

export function localizedField(
  ka: string | null | undefined,
  en: string | null | undefined,
  locale: string
): string {
  const primary = locale === 'ka' ? ka : en;
  const other = locale === 'ka' ? en : ka;
  if (primary && primary.trim()) return primary;
  if (other && other.trim()) return other;
  return '';
}
