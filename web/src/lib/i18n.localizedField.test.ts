import { describe, it, expect } from 'vitest';
import { localizedField } from './i18n';

describe('localizedField', () => {
  it('returns the primary value for the active locale', () => {
    expect(localizedField('გული', 'Heart', 'ka')).toBe('გული');
    expect(localizedField('გული', 'Heart', 'en')).toBe('Heart');
  });
  it('falls back to the other locale when the active one is missing', () => {
    expect(localizedField(null, 'English bio', 'ka')).toBe('English bio');
    expect(localizedField('ქართული', null, 'en')).toBe('ქართული');
  });
  it('treats empty/whitespace as missing', () => {
    expect(localizedField('   ', 'Heart', 'ka')).toBe('Heart');
  });
  it('returns an empty string when both are missing', () => {
    expect(localizedField(null, '', 'ka')).toBe('');
  });
});
