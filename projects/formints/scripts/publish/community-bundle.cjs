#!/usr/bin/env node
/**
 * Community bundle generator.
 *
 * Refreshes the standalone community publish bundle (the public repo
 * github.com/mammhoud/formint-community) from the in-repo Community edition
 * `formint-community/`, applying the Formints Community rename contract:
 *
 *   package name     formint-pos      → formint-community
 *   Tauri product    Formint          → Formints Community
 *   Tauri identifier com.mammhoud.pos → com.mammhoud.formint-community
 *   window title     Formint          → Formints Community
 *
 * The bundle is written to `publish/community-bundle/` (git-ignored staging
 * dir) so the tracked in-repo edition is never touched. Generated artifacts
 * are excluded (node_modules, dist, src-tauri/target, databases, screenshots,
 * reports), and a standalone README.md + .gitignore are written so the folder
 * can be git-initialized and pushed as its own repo.
 *
 * Usage:
 *   node scripts/publish/community-bundle.cjs        (from projects/formints/)
 *   make community-bundle
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..'); // projects/formints/
const SRC = path.join(ROOT, 'formint-community');
const DEST = path.join(ROOT, 'publish', 'community-bundle');

const PRODUCT_NAME = 'Formints Community';
const IDENTIFIER = 'com.mammhoud.formint-community';
const PACKAGE_NAME = 'formint-community';
const REPO_URL = 'https://github.com/mammhoud/formint-community';

// Generated / machine-specific paths that must never ship in the public repo.
// Entries are matched against EVERY path segment, so `target` excludes
// `src-tauri/target`, `dist` excludes any build output, etc.
const EXCLUDE = new Set([
  'node_modules',
  'dist',
  'target',
  'gen',
  'screenshots',
  '.astro',
  'test-results',
  'playwright-report',
  '.venv',
  '.git',
  '.DS_Store',
]);

const EXCLUDE_FILE = (name) =>
  name === 'restaurant.db' ||
  name === 'restaurant.db-shm' ||
  name === 'restaurant.db-wal' ||
  name === 'appmap.log' ||
  name === '.env';

function copyFilter(srcPath) {
  // Match exclusion by ANY path segment (e.g. `src-tauri/target` matches the
  // `target` segment) — basename-only matching would copy multi-GB build dirs.
  const rel = path.relative(SRC, srcPath);
  const segments = rel.split(path.sep);
  if (segments.some((segment) => EXCLUDE.has(segment))) return false;
  const name = path.basename(srcPath);
  if (EXCLUDE_FILE(name)) return false;
  return true;
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function main() {
  if (!fs.existsSync(SRC)) {
    console.error(`source edition not found: ${SRC}`);
    process.exit(1);
  }

  // Wipe the previous bundle so stale files never leak into the public repo.
  fs.rmSync(DEST, { recursive: true, force: true });
  ensureDir(DEST);
  fs.cpSync(SRC, DEST, { recursive: true, filter: copyFilter });

  // ── Rename: package.json ──
  const pkgPath = path.join(DEST, 'package.json');
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
  pkg.name = PACKAGE_NAME;
  pkg.version = pkg.version || '0.1.0';
  pkg.description = 'Formints Community — free, offline-first desktop point of sale (Tauri 2 + Rust/Diesel + React 19).';
  pkg.repository = { type: 'git', url: `${REPO_URL}.git` };
  pkg.homepage = 'https://structa.cloud';
  fs.writeFileSync(pkgPath, JSON.stringify(pkg, null, 2) + '\n');

  // ── Rename: package-lock.json (keep the lock name in sync) ──
  const lockPath = path.join(DEST, 'package-lock.json');
  if (fs.existsSync(lockPath)) {
    const lock = JSON.parse(fs.readFileSync(lockPath, 'utf8'));
    lock.name = PACKAGE_NAME;
    if (lock.packages?.['']) lock.packages[''].name = PACKAGE_NAME;
    fs.writeFileSync(lockPath, JSON.stringify(lock, null, 2) + '\n');
  }

  // ── Rename: tauri.conf.json ──
  const tauriPath = path.join(DEST, 'src-tauri', 'tauri.conf.json');
  const tauri = JSON.parse(fs.readFileSync(tauriPath, 'utf8'));
  tauri.productName = PRODUCT_NAME;
  tauri.identifier = IDENTIFIER;
  if (tauri.app?.windows) {
    for (const win of tauri.app.windows) {
      if (win.title && win.title.toLowerCase().includes('formint')) {
        win.title = PRODUCT_NAME;
      }
    }
  }
  if (tauri.bundle) {
    tauri.bundle.shortDescription = `${PRODUCT_NAME} — Point of Sale System`;
    if (tauri.bundle.longDescription) {
      tauri.bundle.longDescription = `${PRODUCT_NAME} is a free, offline-first point-of-sale system for managing restaurant sales, inventory, analytics, and more. Built with Tauri, React, and Rust.`;
    }
  }
  fs.writeFileSync(tauriPath, JSON.stringify(tauri, null, 2) + '\n');

  // ── Rename: src-tauri/Cargo.toml productName refs (if any) ──
  const cargoPath = path.join(DEST, 'src-tauri', 'Cargo.toml');
  if (fs.existsSync(cargoPath)) {
    let cargo = fs.readFileSync(cargoPath, 'utf8');
    cargo = cargo.replace(/name\s*=\s*"formint-pos"/, `name = "${PACKAGE_NAME}"`);
    cargo = cargo.replace(/productName\s*=\s*"Formint"/, `productName = "${PRODUCT_NAME}"`);
    fs.writeFileSync(cargoPath, cargo);
  }

  // ── Rename: GitHub Actions artifact names (release.yml ships pos-ko_*) ──
  const workflowsDir = path.join(DEST, '.github', 'workflows');
  if (fs.existsSync(workflowsDir)) {
    for (const file of fs.readdirSync(workflowsDir)) {
      const fp = path.join(workflowsDir, file);
      let content = fs.readFileSync(fp, 'utf8');
      if (content.includes('pos-ko')) {
        content = content.replace(/pos-ko_/g, `${PACKAGE_NAME}_`);
        content = content.replace(/pos-ko/g, PACKAGE_NAME);
        fs.writeFileSync(fp, content);
        console.log(`  patched ${file} artifact names → ${PACKAGE_NAME}_*`);
      }
    }
  }

  // ── Rename: shipped docs ──
  // Source docs legitimately reference the in-repo identifier (com.mammhoud.pos)
  // and the old codename (pos-ko), so the public copies must be rewritten.
  // COMMUNITY.md is excluded — it documents the rename mapping itself — and the
  // standalone README is written fresh below, so neither needs patching.
  function patchMarkdown(dir, pattern, to) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const fp = path.join(dir, entry.name);
      if (entry.isSymbolicLink()) continue; // never read/write through links
      if (entry.isDirectory()) {
        if (!EXCLUDE.has(entry.name)) patchMarkdown(fp, pattern, to);
      } else if (
        (entry.name.endsWith('.md') || entry.name.endsWith('.markdown')) &&
        entry.name !== 'COMMUNITY.md'
      ) {
        const content = fs.readFileSync(fp, 'utf8');
        if (pattern.test(content)) {
          fs.writeFileSync(fp, content.replace(new RegExp(pattern.source, 'g'), to));
          console.log(`  patched ${path.relative(DEST, fp)} → ${to}`);
        }
      }
    }
  }
  patchMarkdown(DEST, /\bcom\.mammhoud\.pos\b/, IDENTIFIER);
  patchMarkdown(DEST, /\bpos-ko\b/, PACKAGE_NAME);

  // ── Standalone README (replaces the monorepo one — no ../relative links) ──
  const readme = `# Formints Community

> Free & open-source desktop point of sale — offline-first, single terminal.

<p align="center">
  <img src="https://img.shields.io/badge/license-AGPL--3.0-blue" alt="License"/>
  <img src="https://img.shields.io/badge/version-${pkg.version || '0.1.0'}-green" alt="Version"/>
</p>

**Formints Community** is the open-source, offline-first edition of the
Formints point of sale. Everything runs on one device — no server, no sidecar,
no cloud. Your data stays in a local SQLite database (\`restaurant.db\`).

Built with **Tauri 2 + Rust/Diesel + React 19**.

## Editions

This repository ships the **Community** edition only. The commercial editions
(Standard, Pro, Cloud) live at [structa.cloud](https://structa.cloud) and add an
embedded Python sidecar, multi-terminal cloud sync, a cloud CRM master, and
hosted operations.

## Features

- Offline-first mode — data stays on this device
- Sales, receipting + inventory
- Refunds & returns
- Payment types: cash, card, split
- ESC/POS thermal printer support
- Invoice PDF generation + advanced receipt templates
- i18n: English, French, Arabic (+ more locales)
- Role-based access control — 5 default roles
- Theme system — 5 variants with a Theme Studio
- KDS (Kitchen Display System)

## Quick start

\`\`\`bash
pnpm install
cd src-tauri && cargo fetch && cd ..
pnpm dev          # Vite dev server at localhost:1420
pnpm dev:desktop  # Full Tauri desktop app
\`\`\`

Seed the demo database:

\`\`\`bash
pnpm db:seed   # or: make seed
\`\`\`

## Testing

\`\`\`bash
pnpm test                 # Vitest unit tests
pnpm test:e2e             # Playwright e2e
cd src-tauri && cargo test  # Rust tests
\`\`\`

## Build

\`\`\`bash
pnpm build:desktop  # .dmg / .msi / .AppImage
\`\`\`

## License

**AGPL-3.0** — see [LICENSE](LICENSE). The Community edition is free and open
source; the commercial editions are sold separately at
[structa.cloud](https://structa.cloud).

## Links

- Website: https://structa.cloud
- Source: ${REPO_URL}
`;
  fs.writeFileSync(path.join(DEST, 'README.md'), readme);

  // ── Standalone .gitignore ──
  const gitignore = `# Dependencies
node_modules/

# Build output
dist/
src-tauri/target/
src-tauri/gen/
.astro/

# Local data
restaurant.db
restaurant.db-*
.env

# Tests
test-results/
playwright-report/
e2e/screenshots/

# Misc
.DS_Store
appmap.log
`;
  fs.writeFileSync(path.join(DEST, '.gitignore'), gitignore);

  // ── Source marker ──
  fs.writeFileSync(
    path.join(DEST, 'COMMUNITY.md'),
    `# Generated bundle — do not edit directly

\`publish/community-bundle/\` is generated from the Community edition
\`projects/formints/formint-community/\` by \`make community-bundle\`
(\`scripts/publish/community-bundle.cjs\`), which applies the rename contract:

| Field | In-repo | Community version |
|-------|---------|-------------------|
| package name | \`formint-community\` | \`formint-community\` |
| Tauri product | Formints Community | ${PRODUCT_NAME} |
| Tauri identifier | \`com.mammhoud.formint-community\` | \`${IDENTIFIER}\` |
| window title | Formints Community | ${PRODUCT_NAME} |

Make feature changes in \`formint-community/\`, then run \`make community-bundle\` to
refresh this folder. To publish: \`git init\`, commit, and push to ${REPO_URL}.
`,
  );

  console.log(`✓ community bundle refreshed from formint-community`);
  console.log(`  product:    ${PRODUCT_NAME}`);
  console.log(`  identifier: ${IDENTIFIER}`);
  console.log(`  destination: ${DEST}`);
  console.log(`  (staging dir — git-init and push to ${REPO_URL} to publish)`);
}

main();
