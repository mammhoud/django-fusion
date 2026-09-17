// Translation completeness is a build-time property, not a UI behaviour, so it
// is asserted directly against the catalogue and the markup. Every locale must
// carry exactly the same keys, and every `data-i18n*` hook in index.html must
// resolve in both locales — otherwise new copy ships half-translated.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { test, expect } from '@playwright/test';
import { translations, locales } from '../public/i18n.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const html = fs.readFileSync(path.join(__dirname, '..', 'public', 'index.html'), 'utf8');

const attributeNames = ['data-i18n', 'data-i18n-title', 'data-i18n-placeholder', 'data-i18n-content', 'data-i18n-aria-label'];

test('every locale carries the same translation keys', () => {
  const reference = Object.keys(translations.en).sort();
  for (const locale of locales) {
    const keys = Object.keys(translations[locale] || {}).sort();
    const missing = reference.filter((key) => !keys.includes(key));
    const extra = keys.filter((key) => !reference.includes(key));
    expect({ locale, missing, extra }).toEqual({ locale, missing: [], extra: [] });
    for (const key of reference) {
      expect(translations[locale][key].length, `${locale}.${key} is empty`).toBeGreaterThan(0);
    }
  }
});

test('every data-i18n hook in the shell resolves in both locales', () => {
  const keys = new Set();
  for (const attribute of attributeNames) {
    const pattern = new RegExp(`${attribute}="([^"]+)"`, 'g');
    for (const match of html.matchAll(pattern)) keys.add(match[1]);
  }
  expect(keys.size).toBeGreaterThan(100);
  const unresolved = [...keys].filter((key) => locales.some((locale) => !translations[locale]?.[key]));
  expect(unresolved).toEqual([]);
});

test('the Arabic catalogue is actually translated, not copied from English', () => {
  const untranslated = Object.keys(translations.en).filter((key) => translations.ar[key] === translations.en[key]
    // Identifiers, shortcut hints and glyph-only labels stay identical by design.
    && /[A-Za-z]{4,}/.test(translations.en[key])
    && !/^(my-prompt|gpt-4o-mini|https)/.test(translations.en[key])
    && !translations.en[key].startsWith('{'));
  expect(untranslated).toEqual([]);
});
