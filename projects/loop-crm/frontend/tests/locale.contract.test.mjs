import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import assert from 'node:assert/strict';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');

const read = (relativePath) => readFile(resolve(ROOT, relativePath), 'utf8');

test('locale selector uses the canonical API and CSRF-protected persistence', async () => {
  const island = await read('src/components/dashboard/LocaleSwitcher.tsx');
  const shell = await read('src/components/AppShell.astro');
  const api = await read('../backend/apps/core/locale_api.py');
  const urls = await read('../backend/apps/core/apis_core_urls.py');

  assert.match(shell, /LocaleSwitcher client:load/);
  assert.match(island, /\/apis\/core\/locale\//);
  assert.match(island, /X-CSRFToken/);
  assert.match(island, /document\.documentElement\.dir/);
  assert.match(api, /LANGUAGE_COOKIE_NAME/);
  assert.match(api, /supported/);
  assert.match(urls, /path\("locale\//);
});

test('locale selector exposes the supported bilingual direction contract', async () => {
  const api = await read('../backend/apps/core/locale_api.py');
  const settings = await read('../backend/configs/default/__init__.py');

  assert.match(settings, /\("en", "English"\)/);
  assert.match(settings, /\("ar", "العربية"\)/);
  assert.match(api, /"rtl" if code\.split/);
});
