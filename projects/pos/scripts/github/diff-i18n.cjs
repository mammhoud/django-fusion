#!/usr/bin/env node
/**
 * scripts/github/diff-i18n.cjs
 *
 * Compares translation-key parity between two checkouts.
 *
 *   node scripts/github/diff-i18n.cjs <base-dir> <head-dir>
 *
 * For each non-reference locale (fr, ar), computes the set of keys missing
 * compared to the English reference in BOTH <base-dir> and <head-dir>, then
 * reports any keys that are MISSING in <head-dir> but were PRESENT in
 * <base-dir>. The script exits 0 if no new missing keys were introduced, or
 * 1 if any locale has new gaps.
 *
 * Designed for PR-time CI via `.github/workflows/i18n.yml`: catches the case
 * where a PR adds a new en.json key without translating it into fr/ar.
 * Pre-existing gaps do not fail the build (those are tracked separately in
 * docs/i18n-gaps.md).
 *
 * Note: this script detects NEW missing keys only. A PR that REMOVES a fr/ar
 * translation that was previously present will not be flagged by this check.
 * Translation removal is tracked separately by code review conventions.
 *
 * Exit codes:
 *   0  — head introduces no new missing keys
 *   1  — head has new missing keys (GitHub Actions failure markers emitted)
 *   2  — bad invocation (wrong args, missing dirs, malformed JSON)
 */
'use strict';

const fs = require('fs');
const path = require('path');

const LOCALES = ['fr', 'ar'];
const REFERENCE = 'en';

function fail(message, code = 2) {
  console.error(`::error::${message}`);
  process.exit(code);
}

function flatten(obj, prefix = []) {
  return Object.entries(obj || {}).flatMap(([key, value]) => {
    const p = [...prefix, key];
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      return flatten(value, p);
    }
    return [p.join('.')];
  });
}

function readLocale(locale, dir) {
  const file = path.join(dir, 'src', 'i18n', `${locale}.json`);
  let raw;
  try {
    raw = fs.readFileSync(file, 'utf8');
  } catch (err) {
    fail(`Cannot read ${file}: ${err.message}`);
  }
  try {
    return JSON.parse(raw);
  } catch (err) {
    fail(`Malformed JSON in ${file}: ${err.message}`);
  }
}

function missingKeys(locale, dir) {
  const refSet = new Set(flatten(readLocale(REFERENCE, dir)));
  const locSet = new Set(flatten(readLocale(locale, dir)));
  return [...refSet].filter((k) => !locSet.has(k)).sort();
}

const [, , baseArg, headArg] = process.argv;
if (!baseArg || !headArg) {
  console.error('Usage: node scripts/github/diff-i18n.cjs <base-dir> <head-dir>');
  process.exit(2);
}

if (!fs.existsSync(baseArg)) fail(`base dir not found: ${baseArg}`, 2);
if (!fs.existsSync(headArg)) fail(`head dir not found: ${headArg}`, 2);

let exitCode = 0;
const regressions = [];

console.log(`Comparing ${baseArg} -> ${headArg}\n`);

for (const locale of LOCALES) {
  const baseMissing = missingKeys(locale, baseArg);
  const headMissing = missingKeys(locale, headArg);
  const baseSet = new Set(baseMissing);
  const newlyMissing = headMissing.filter((k) => !baseSet.has(k));
  const fixedPreviouslyMissing = baseMissing.filter((k) => !headMissing.includes(k));

  console.log(
    `[${locale}] base missing: ${baseMissing.length} | ` +
    `head missing: ${headMissing.length} | ` +
    `newly missing: ${newlyMissing.length} | ` +
    `fixed: ${fixedPreviouslyMissing.length}`,
  );

  if (newlyMissing.length > 0) {
    const fileParam = `file=src/i18n/${locale}.json`;
    const titleParam = `title=i18n: new missing keys (${locale})`;
    const headerMsg = `${locale}: ${newlyMissing.length} new missing key(s) introduced by this PR`;
    console.error(`\n::error ${fileParam},${titleParam}::${headerMsg}`);
    for (const key of newlyMissing) {
      console.error(`::error ${fileParam},${titleParam}::  - ${key}`);
    }
    regressions.push({ locale, keys: newlyMissing });
    exitCode = 1;
  }
}

if (exitCode === 1) {
  const total = regressions.reduce((n, r) => n + r.keys.length, 0);
  console.error(
    `\nThis PR introduces ${total} new missing translation ` +
    `key(s). Add translations to src/i18n/{${LOCALES.join(',')}}.json or update the existing ` +
    `filler scripts in scripts/fill-{fr,ar}-translations.cjs.`,
  );
  console.error('Full gap report is committed in docs/i18n-gaps.md.');
} else if (regressions.length === 0) {
  console.log('\n\u2713 No new missing translation keys introduced.');
}

process.exit(exitCode);
