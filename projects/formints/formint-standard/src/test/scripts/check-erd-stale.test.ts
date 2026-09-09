/**
 * Tests for the ERD staleness check (scripts/check-erd-stale.mjs).
 *
 * Verifies the CI-style behaviour:
 * 1. Passes (exit 0) when docs/erd is in sync with schema.rs + operations/
 * 2. Fails (exit 1, with a "stale" message) when a source changed but the
 *    generated docs were not regenerated
 * 3. Also fails when an operations module's functions change
 *
 * The test regenerates docs/erd from current sources, mutates a source file to
 * simulate drift, re-runs the check, then restores the source file exactly.
 * It skips the mutation cases when the repo already has uncommitted changes to
 * the source files (the check compares against the working tree, not HEAD).
 */
import { describe, it, expect, beforeAll } from 'vitest';
import { execFileSync, execSync } from 'child_process';
import { readFileSync, writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const ROOT = resolve(__dirname, '../../..');
const CHECK = resolve(ROOT, 'scripts/check-erd-stale.mjs');
const GENERATOR = resolve(ROOT, 'scripts/generate-erd.mjs');
const SCHEMA = resolve(ROOT, 'src-tauri/src/db/schema.rs');
const OPS_DIR = resolve(ROOT, 'src-tauri/src/operations');

function runCheck() {
  return execFileSync(process.execPath, [CHECK], { cwd: ROOT, encoding: 'utf8' });
}

/** A source file is "clean" in git when the working tree matches HEAD. */
function isGitClean(rel: string): boolean {
  try {
    const out = execSync(`git status --porcelain -- "${rel}"`, { cwd: ROOT, encoding: 'utf8' });
    return out.trim().length === 0;
  } catch {
    return false;
  }
}

describe('ERD staleness check (scripts/check-erd-stale.mjs)', () => {
  beforeAll(() => {
    // Baseline: docs/erd must be in sync with the current sources.
    execFileSync(process.execPath, [GENERATOR], { cwd: ROOT, stdio: 'pipe' });
  });

  it('passes (exit 0) when docs/erd is up to date', () => {
    expect(() => runCheck()).not.toThrow();
  });

  it('fails (exit 1) when schema.rs changes without regenerating docs/erd', () => {
    if (!isGitClean('src-tauri/src/db/schema.rs')) {
      console.warn('SKIP: schema.rs already has uncommitted changes in this workspace.');
      return;
    }
    const original = readFileSync(SCHEMA, 'utf8');
    const mutated = original.replace('exchange_rate -> Double,', 'exchange_rate -> Integer,');
    expect(mutated, 'test mutation must be a real change').not.toBe(original);
    writeFileSync(SCHEMA, mutated);
    try {
      let msg = '';
      let code = 0;
      try {
        runCheck();
      } catch (err) {
        msg = String(err && err.stdout ? err.stdout : err);
        code = (err as { status?: number }).status ?? 1;
      }
      expect(code).not.toBe(0);
      expect(msg).toContain('stale');
    } finally {
      writeFileSync(SCHEMA, original);
    }
  });

  it('fails (exit 1) when an operations module function changes without regenerating', () => {
    if (!isGitClean('src-tauri/src/operations/currency.rs')) {
      console.warn('SKIP: operations/currency.rs already has uncommitted changes in this workspace.');
      return;
    }
    const opsFile = resolve(OPS_DIR, 'currency.rs');
    const original = readFileSync(opsFile, 'utf8');
    // Adding a real exported function changes the generated function inventory.
    const marker = '\n// stale-check-test\npub fn list_currencies_stale_check_test() -> Result<(), String> { Ok(()) }\n';
    writeFileSync(opsFile, original + marker);
    try {
      let msg = '';
      let code = 0;
      try {
        runCheck();
      } catch (err) {
        msg = String(err && err.stdout ? err.stdout : err);
        code = (err as { status?: number }).status ?? 1;
      }
      expect(code).not.toBe(0);
      expect(msg).toContain('stale');
    } finally {
      writeFileSync(opsFile, original);
    }
  });

  it('reports up-to-date status after regeneration', () => {
    // Regenerate after the mutation tests restored the sources.
    execFileSync(process.execPath, [GENERATOR], { cwd: ROOT, stdio: 'pipe' });
    expect(() => runCheck()).not.toThrow();
  });
});