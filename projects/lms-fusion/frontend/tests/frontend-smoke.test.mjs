import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const root = new URL('../', import.meta.url);
const text = async (path) => readFile(new URL(path, root), 'utf8');

test('Astro frontend exposes the consolidated LMS contract', async () => {
  const packageJson = JSON.parse(await text('package.json'));
  assert.equal(packageJson.name, 'lms-fusion-astro');
  assert.equal(packageJson.scripts.build, 'astro build');
  assert.equal(packageJson.scripts.check, 'astro check');

  const api = await text('src/lib/api.ts');
  assert.match(api, /PUBLIC_FUSION_API_URL/);
  assert.match(api, /\/apis\/pages\//);

  const layout = await text('src/layouts/Layout.astro');
  assert.match(layout, /htmx-indicator-skeleton/);
  assert.match(layout, /fusion-skeleton__card/);

  const skeleton = await text('src/components/ui/Skeleton.astro');
  assert.match(skeleton, /hero-section/);
  assert.match(skeleton, /faq-list/);
});
