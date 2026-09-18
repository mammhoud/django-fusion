#!/usr/bin/env node
/**
 * CI-style staleness check for the ERD documentation.
 *
 * Regenerates docs/erd/erd-data.js + docs/erd/erd.mmd from the current
 * schema/operations sources into a temp directory and compares them with the
 * files in the working tree. Exits non-zero (with the diff) when they drift —
 * i.e. when src-tauri/src/db/schema.rs or src-tauri/src/operations/*.rs
 * changed but docs/erd was not regenerated.
 *
 * Usage: node scripts/check-erd-stale.mjs
 * Exit:  0 = up to date, 1 = stale (diff printed), 2 = other error
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, rmSync, readdirSync, readFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { resolve, dirname, join, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const ERD_DIR = resolve(ROOT, 'docs/erd');
const CHECKED_FILES = ['erd-data.js', 'erd.mmd'];

function log(msg) {
  // eslint-disable-next-line no-console
  console.log(msg);
}

function fail(msg) {
  // eslint-disable-next-line no-console
  console.error(msg);
  process.exit(1);
}

try {
  // 1. Regenerate into a throwaway directory.
  const tmp = mkdtempSync(join(tmpdir(), 'formint-erd-check-'));
  const { generate } = await import('./generate-erd.mjs');
  generate({ outDir: tmp, quiet: true });

  // 2. Compare with the tracked files.
  const dirty = [];
  for (const f of CHECKED_FILES) {
    const fresh = readFileSync(join(tmp, f), 'utf8');
    const path = join(ERD_DIR, f);
    if (!existsSync(path)) {
      dirty.push(f);
      log(`✗ ${f} is missing — run \`node scripts/generate-erd.mjs\` and commit it.`);
      continue;
    }
    const tracked = readFileSync(path, 'utf8');
    if (fresh !== tracked) {
      dirty.push(f);
      log(`✗ ${f} is stale — regenerate with \`node scripts/generate-erd.mjs\`.`);
      try {
        const diff = execFileSync('git', ['diff', '--no-index', '--', path, join(tmp, f)], {
          cwd: ROOT,
          encoding: 'utf8',
          maxBuffer: 1024 * 1024 * 4,
        });
        log(diff.slice(0, 4000));
      } catch {
        // git diff --no-index exits 1 when files differ — that's the signal.
      }
    }
  }

  // 3. Also report files that exist in docs/erd but are no longer generated
  //    (e.g. a rename removed one of the outputs).
  const generatedNames = new Set(CHECKED_FILES);
  for (const f of readdirSync(ERD_DIR)) {
    if (f.endsWith('.js') || f.endsWith('.mmd')) {
      if (!generatedNames.has(f) && f !== 'erd-data.js' && f !== 'erd.mmd') {
        log(`✗ unexpected generated artifact ${f} in docs/erd — check scripts/generate-erd.mjs.`);
        dirty.push(f);
      }
    }
  }

  rmSync(tmp, { recursive: true, force: true });

  if (dirty.length) {
    fail(`\n✗ ERD docs are out of date (${dirty.join(', ')}).\n  Run \`node scripts/generate-erd.mjs\` and commit the regenerated files.`);
  }
  log('✓ docs/erd is up to date with schema.rs and operations/.');
  process.exit(0);
} catch (err) {
  fail(`✗ ERD staleness check failed: ${err && err.message ? err.message : err}`);
}