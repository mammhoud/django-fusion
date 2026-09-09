/**
 * Tests for the ERD generator script (scripts/generate-erd.mjs).
 *
 * Verifies that regenerating the docs/erd outputs stays consistent with the
 * source schema:
 * 1. All diesel::table! entities in schema.rs are emitted
 * 2. Relations are unique, correctly directed (parent ||--o{ child) and only
 *    reference existing entities
 * 3. Every entity has a domain + operations logic note
 * 4. Every entity is present in the mermaid diagram
 */
import { describe, it, expect } from 'vitest';
import { execFileSync } from 'child_process';
import { readFileSync, existsSync, readdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const ROOT = resolve(__dirname, '../../..');
const SCHEMA_PATH = resolve(ROOT, 'src-tauri/src/db/schema.rs');
const GENERATOR = resolve(ROOT, 'scripts/generate-erd.mjs');
const DATA_PATH = resolve(ROOT, 'docs/erd/erd-data.js');
const MMD_PATH = resolve(ROOT, 'docs/erd/erd.mmd');

/** Count entities declared in schema.rs via diesel::table! macros. */
function countSchemaTables() {
  const src = readFileSync(SCHEMA_PATH, 'utf8');
  return (src.match(/diesel::table!\s*\{/g) ?? []).length;
}

/** Load the generated ERD data (data file assigns window.ERD_DATA). */
function loadErdData() {
  globalThis.window = globalThis.window ?? {};
  eval(readFileSync(DATA_PATH, 'utf8'));
  return globalThis.window.ERD_DATA;
}

describe('ERD generator (scripts/generate-erd.mjs)', () => {
  beforeAll(() => {
    expect(existsSync(GENERATOR), 'generator script must exist').toBe(true);
    expect(existsSync(SCHEMA_PATH), 'schema.rs must exist').toBe(true);
    execFileSync(process.execPath, [GENERATOR], { cwd: ROOT, stdio: 'pipe' });
  });

  it('emits every entity from schema.rs', () => {
    const data = loadErdData();
    expect(data.entities.length).toBe(countSchemaTables());
    expect(data.stats.tables).toBe(data.entities.length);
  });

  it('emits only unique relations', () => {
    const data = loadErdData();
    const keys = data.relations.map((r) => `${r.child}|${r.parent}|${r.column}`);
    expect(new Set(keys).size).toBe(keys.length);
  });

  it('relations only reference existing entities and have declared FK columns', () => {
    const data = loadErdData();
    const names = new Set(data.entities.map((e) => e.name));
    for (const r of data.relations) {
      expect(names.has(r.parent), `parent ${r.parent} must exist`).toBe(true);
      expect(names.has(r.child), `child ${r.child} must exist`).toBe(true);
      const child = data.entities.find((e) => e.name === r.child);
      const col = child.columns.find((c) => c.name === r.column);
      expect(col, `${r.child}.${r.column} must be a declared column`).toBeTruthy();
    }
  });

  it('every entity has a domain and an operations logic note', () => {
    const data = loadErdData();
    for (const e of data.entities) {
      expect(e.domain, `${e.name} domain`).toBeTruthy();
      expect(e.logic, `${e.name} logic note`).toBeTruthy();
    }
  });

  it('mermaid diagram contains every entity and correct relation direction', () => {
    const data = loadErdData();
    const mmd = readFileSync(MMD_PATH, 'utf8');
    for (const e of data.entities) {
      expect(mmd, `mmd must define ${e.name}`).toContain(`    ${e.name} {`);
    }
    // parent ||--o{ child : "fk_column" — one line per relation
    for (const r of data.relations) {
      const line = `    ${r.parent} ||--o{ ${r.child} : "${r.column}"`;
      expect(mmd, `mmd must contain ${line}`).toContain(line);
    }
  });

  it('every operations module listed for an entity exists on disk', () => {
    const data = loadErdData();
    const opsDir = resolve(ROOT, 'src-tauri/src/operations');
    const files = new Set(readdirSync(opsDir));
    for (const e of data.entities) {
      for (const op of e.operations) {
        expect(files.has(`${op.module}.rs`), `${op.file} must exist`).toBe(true);
      }
    }
  });
});