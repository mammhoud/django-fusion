#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Current year
const currentYear = new Date().getFullYear();

// Resolve project root: use PROJECT_ROOT env var if set, otherwise use parent of parent
const projectRoot = process.env.PROJECT_ROOT || process.cwd();

// Update tauri.conf.json — but only if the year actually changed, to avoid
// triggering Tauri's file watcher unnecessarily (which causes recompilation loops).
const tauriConfigPath = path.join(projectRoot, 'src-tauri/tauri.conf.json');

if (!fs.existsSync(tauriConfigPath)) {
  console.log(`update-year: tauri.conf.json not found at ${tauriConfigPath} — skipping`);
  process.exit(0);
}

const tauriConfig = JSON.parse(fs.readFileSync(tauriConfigPath, 'utf8'));

const expectedCopyright = `© ${currentYear} Structa Cloud. All rights reserved.`;
if (tauriConfig.bundle?.copyright === expectedCopyright) {
  console.log(`✅ Copyright year already up-to-date (${currentYear})`);
  process.exit(0);
}

// Update copyright with current year
if (tauriConfig.bundle) {
  tauriConfig.bundle.copyright = expectedCopyright;
}

// Write back to file
fs.writeFileSync(tauriConfigPath, JSON.stringify(tauriConfig, null, 2) + '\n');

console.log(`✅ Updated copyright year to ${currentYear}`);
