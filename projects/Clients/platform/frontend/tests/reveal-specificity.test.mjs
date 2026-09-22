/**
 * Reveal-specificity regression — the course detail `.reveal-up` scroll reveal.
 *
 * Pure source-file contract test (no build, no backend): the hidden state
 * `.js .reveal-up` (two classes) must never out-specify the visible state
 * `.js .reveal-up.reveal-up--visible` (three classes). When it did, every
 * section stayed at `opacity: 0` even after the observer fired.
 *
 * Run:  npm test
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const read = (path) => readFile(join(root, path), 'utf8');

const classCount = (selector) => (selector.match(/\./g) ?? []).length;

test('course page reveal-visible rule out-specifies the hidden state (regression)', async () => {
  const detail = await read('src/pages/courses/[slug].astro');

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

test('global safety net keeps reveal content readable without JS or Alpine', async () => {
  const globals = await read('src/styles/globals.css');

  // The progressive-enhancement net forces every reveal class visible when
  // `.js` is absent (no JS) or `fusion-motion-ready` is absent (Alpine never
  // booted) — the counterweight to the motion-gated hidden states.
  assert.match(
    globals,
    /html:not\(\.js\) \.reveal-up/,
    'the no-JS fallback should cover the course-page reveal-up class',
  );
  assert.match(
    globals,
    /html:not\(\.js\) \.features__card/,
    'the no-JS fallback should cover card blocks like .features__card',
  );
});
