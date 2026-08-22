import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const root = new URL('../', import.meta.url);
const text = async (path) => readFile(new URL(path, root), 'utf8');

test('Astro frontend exposes the consolidated LMS contract', async () => {
  const packageJson = JSON.parse(await text('package.json'));
  assert.equal(packageJson.name, 'precis-lms-astro');
  assert.equal(packageJson.scripts.build, 'astro build');
  assert.equal(packageJson.scripts.check, 'astro check');

  const api = await text('src/lib/api.ts');
  assert.match(api, /PUBLIC_FUSION_API_URL/);
  assert.match(api, /\/apis\/pages\//);
  assert.match(api, /\/api\/courses\//);

  const layout = await text('src/layouts/Layout.astro');
  assert.match(layout, /htmx-indicator-skeleton/);
  assert.match(layout, /fusion-skeleton__card/);

  const skeleton = await text('src/components/ui/Skeleton.astro');
  assert.match(skeleton, /hero-section/);
  assert.match(skeleton, /faq-list/);

  const catalog = await text('src/pages/courses/index.astro');
  assert.match(catalog, /fetchCourseList/);
  assert.match(catalog, /medical learning|clinical research/i);

  const detail = await text('src/pages/courses/[slug].astro');
  assert.match(detail, /fetchCourseDetail/);
  assert.match(detail, /course overview/);
});

test('course detail reveal-visible rule out-specifies the hidden state (regression)', async () => {
  // Guards the scroll-reveal specificity bug: `.js .reveal-up` (two classes)
  // used to out-specify the single-class `.reveal-up--visible` (one class),
  // so every section stayed at opacity 0 even after the observer fired. The
  // visible rule must carry BOTH classes to win the cascade.
  const detail = await text('src/pages/courses/[slug].astro');

  assert.match(
    detail,
    /\.js \.reveal-up\s*\{[^}]*opacity:\s*0/,
    'hidden rule `.js .reveal-up { opacity: 0 }` should exist',
  );
  assert.match(
    detail,
    /\.js \.reveal-up\.reveal-up--visible\s*\{[^}]*opacity:\s*1/,
    'visible rule `.js .reveal-up.reveal-up--visible { opacity: 1 }` should exist',
  );

  const classCount = (selector) => (selector.match(/\./g) ?? []).length;
  assert.ok(
    classCount('.js .reveal-up.reveal-up--visible') > classCount('.js .reveal-up'),
    "the visible selector must out-specify the hidden selector, otherwise `.js .reveal-up` keeps sections at opacity 0 forever",
  );

  // The higher-specificity selector must also appear in the reduced-motion
  // override (once for the visible rule, once for the media query).
  const occurrences = (detail.match(/\.js \.reveal-up\.reveal-up--visible/g) ?? []).length;
  assert.ok(
    occurrences >= 2,
    'the higher-specificity selector should appear in both the visible rule and the reduced-motion override',
  );
});
