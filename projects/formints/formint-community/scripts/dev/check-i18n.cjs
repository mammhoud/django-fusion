#!/usr/bin/env node
/**
 * i18n key validator — checks that all locale files have matching keys with en.json.
 *
 * Usage:
 *   node scripts/dev/check-i18n.cjs           # write report to docs/i18n-gaps.md
 *   node scripts/dev/check-i18n.cjs --check   # exit 1 if any gaps exist (CI mode)
 *
 * The script:
 *   1. Reads src/i18n/en.json as the reference key set.
 *   2. For each other locale (ar.json, de.json, es.json, fr.json), recursively
 *      collects every key path and compares against en.json.
 *   3. Reports keys present in en.json but missing from the locale (gaps),
 *      and keys present in the locale but absent from en.json (orphans).
 *   4. In --check mode, exits with code 1 if any gaps exist.
 *   5. In audit mode, writes a markdown report to docs/i18n-gaps.md.
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '../..');
const I18N_DIR = path.join(ROOT, 'src', 'i18n');
const GAPS_PATH = path.join(ROOT, 'docs', 'i18n-gaps.md');

const isCheckMode = process.argv.includes('--check');

// ── Helpers ──────────────────────────────────────────────────────────────

/** Recursively collect all leaf key paths from a nested object. */
function flattenKeys(obj, prefix = '') {
  const keys = new Set();
  for (const [k, v] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${k}` : k;
    if (v !== null && typeof v === 'object' && !Array.isArray(v)) {
      for (const child of flattenKeys(v, fullKey)) {
        keys.add(child);
      }
    } else {
      keys.add(fullKey);
    }
  }
  return keys;
}

/** Load and parse a JSON file, returning null on error. */
function loadJSON(filePath) {
  try {
    const raw = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(raw);
  } catch (err) {
    console.error(`  ✗ Failed to load ${path.basename(filePath)}: ${err.message}`);
    return null;
  }
}

/** Human-friendly locale label. */
function localeLabel(code) {
  const labels = {
    en: 'English (reference)',
    ar: 'العربية',
    fr: 'Français',
    de: 'Deutsch',
    es: 'Español',
  };
  return labels[code] || code;
}

// ── Main ────────────────────────────────────────────────────────────────

function main() {
  const localeFiles = ['ar.json', 'de.json', 'es.json', 'fr.json'];
  let hasErrors = false;
  const reportLines = [];
  const gapCounts = {};

  // Load reference (en.json)
  const enRef = loadJSON(path.join(I18N_DIR, 'en.json'));
  if (!enRef) {
    process.exit(1);
  }
  const refKeys = flattenKeys(enRef);

  reportLines.push('# i18n Gaps Report');
  reportLines.push('');
  reportLines.push(`Reference: \`en.json\` (${refKeys.size} keys)`);
  reportLines.push(`Generated: ${new Date().toISOString().split('T')[0]}`);
  reportLines.push('');
  reportLines.push('| Locale | Missing keys | Orphan keys | Status |');
  reportLines.push('|--------|-------------|-------------|--------|');

  for (const file of localeFiles) {
    const filePath = path.join(I18N_DIR, file);
    if (!fs.existsSync(filePath)) {
      reportLines.push(`| \`${file}\` | — | — | ⚠️  File not found |`);
      hasErrors = true;
      continue;
    }

    const locale = loadJSON(filePath);
    if (!locale) {
      reportLines.push(`| \`${file}\` | — | — | 💥 Parse error |`);
      hasErrors = true;
      continue;
    }

    const localeKeys = flattenKeys(locale);
    const missing = [...refKeys].filter(k => !localeKeys.has(k));
    const orphans = [...localeKeys].filter(k => !refKeys.has(k));

    gapCounts[file] = missing.length;

    if (missing.length > 0 || orphans.length > 0) {
      hasErrors = true;
      reportLines.push(`| \`${file}\` ${localeLabel(file.replace('.json', ''))} | ${missing.length} | ${orphans.length} | ❌ Gaps found |`);
    } else {
      reportLines.push(`| \`${file}\` ${localeLabel(file.replace('.json', ''))} | 0 | 0 | ✅ Complete |`);
    }

    // Detail sections for gaps
    if (missing.length > 0) {
      reportLines.push('');
      reportLines.push(`### ${file} — Missing keys (${missing.length})`);
      reportLines.push('');
      reportLines.push('```');
      missing.sort().forEach(k => reportLines.push(k));
      reportLines.push('```');
    }
    if (orphans.length > 0) {
      reportLines.push('');
      reportLines.push(`### ${file} — Orphan keys (${orphans.length})`);
      reportLines.push('');
      reportLines.push('```');
      orphans.sort().forEach(k => reportLines.push(k));
      reportLines.push('```');
    }
  }

  // Summary
  reportLines.push('');
  const totalGaps = Object.values(gapCounts).reduce((a, b) => a + b, 0);
  if (totalGaps === 0) {
    reportLines.push('**✅ All locales are in sync with en.json.**');
  } else {
    reportLines.push(`**❌ ${totalGaps} missing key(s) found across all locales.**`);
  }
  reportLines.push('');

  // Output
  const report = reportLines.join('\n');

  if (isCheckMode) {
    // CI mode: log to stdout and exit with error if gaps exist
    console.log(report);
    if (hasErrors) {
      console.error(`\n❌ i18n check failed: ${totalGaps} missing key(s) found.`);
      process.exit(1);
    }
    console.log('\n✅ i18n check passed — all locales are complete.');
    process.exit(0);
  } else {
    // Audit mode: write report to docs/i18n-gaps.md
    const docsDir = path.dirname(GAPS_PATH);
    if (!fs.existsSync(docsDir)) {
      fs.mkdirSync(docsDir, { recursive: true });
    }
    fs.writeFileSync(GAPS_PATH, report, 'utf8');
    console.log(`✓ i18n audit report written to ${GAPS_PATH}`);
    if (hasErrors) {
      console.log(`  ${totalGaps} missing key(s) found.`);
      process.exit(0); // audit mode doesn't fail
    }
  }
}

main();
