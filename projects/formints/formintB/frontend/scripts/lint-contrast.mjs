#!/usr/bin/env node

/**
 * lint-contrast.mjs
 *
 * Scans .tsx files for `bg-{semantic} text-white` patterns that should use
 * `text-{semantic}-content` instead for theme-aware contrast.
 *
 * Usage: node scripts/lint-contrast.mjs [--fix]
 *
 * Without --fix: reports violations with file:line:col format.
 * With --fix:    replaces `text-white` with `text-{semantic}-content` inline.
 *
 * Exit code: 0 if clean, 1 if violations found (without --fix).
 */

import { readFileSync, writeFileSync, readdirSync } from 'fs';
import { join, extname } from 'path';

const ROOT_DIR = process.cwd();
const SEMANTIC_COLORS = [
  'primary',
  'secondary',
  'info',
  'success',
  'warning',
  'error',
  'neutral',
];

const FIX = process.argv.includes('--fix');
let exitCode = 0;
let fixedCount = 0;
let violationCount = 0;

/** Walk a directory tree and collect .tsx file paths (excluding test files). */
function collectTsxFiles(dir) {
  const results = [];
  let entries;
  try {
    entries = readdirSync(dir, { withFileTypes: true });
  } catch {
    return results;
  }
  for (const entry of entries) {
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === 'node_modules' || entry.name === 'test' || entry.name.startsWith('.')) continue;
      results.push(...collectTsxFiles(fullPath));
    } else if (
      entry.isFile() &&
      extname(entry.name) === '.tsx' &&
      !entry.name.endsWith('.test.tsx') &&
      !entry.name.endsWith('.spec.tsx')
    ) {
      results.push(fullPath);
    }
  }
  return results;
}

/**
 * Check if a line has a bare bg-{semantic} or border-{semantic} class
 * (not bg-{semantic}-500 or similar shade variants).
 * Uses a word-boundary lookahead to avoid matching Tailwind shade scales.
 */
function findSemanticColor(line) {
  for (const c of SEMANTIC_COLORS) {
    const bgRe = new RegExp(`bg-${c}(?:[^-/]|$)`);
    const borderRe = new RegExp(`border-${c}(?:[^-]|$)`);
    if (bgRe.test(line) || borderRe.test(line)) return c;
  }
  return null;
}

/** Replace the first `text-white` with `text-{semantic}-content`. */
function fixLine(line, semantic) {
  return line.replace(/\btext-white\b/, `text-${semantic}-content`);
}

async function main() {
  const srcDir = join(ROOT_DIR, 'src');
  const files = collectTsxFiles(srcDir);

  console.log(`\n🔍 Scanning ${files.length} .tsx files for bg-{semantic} + text-white violations...\n`);

  for (const file of files) {
    const content = readFileSync(file, 'utf-8');
    const lines = content.split('\n');
    const relative = file.replace(ROOT_DIR + '/', '');
    let fileModified = false;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const lineNum = i + 1;

      // Must contain both a bg-{semantic} (or border-{semantic}) AND text-white
      // Skip variant prefixes (hover:, dark:, group-hover:) — those are intentional
      if (!line.includes('text-white') || /:text-white/.test(line)) continue;
      const semantic = findSemanticColor(line);
      if (!semantic) continue;

      // Skip if the file already has a dark-mode override that darkens the bg
      // (e.g., `dark:bg-primary/30 text-white` — the dark variant is darker)
      if (line.includes(`dark:bg-${semantic}/`)) continue;

      const col = line.indexOf('text-white') + 1;
      const snippet = line.trim().substring(0, 80).replace(/\s+/g, ' ');

      if (FIX) {
        const fixed = fixLine(line, semantic);
        lines[i] = fixed;
        fileModified = true;
        fixedCount++;
        console.log(`  ✓ ${relative}:${lineNum}:${col}`);
        console.log(`     ${snippet}`);
        console.log(`     → text-${semantic}-content`);
      } else {
        exitCode = 1;
        violationCount++;
        console.log(`  ✗ ${relative}:${lineNum}:${col}`);
        console.log(`     ${snippet}`);
        console.log(`     → use text-${semantic}-content instead of text-white`);
      }
      console.log('');
    }

    if (FIX && fileModified) {
      writeFileSync(file, lines.join('\n'), 'utf-8');
    }
  }

  if (exitCode === 0) {
    if (FIX && fixedCount > 0) {
      console.log(`✅ Fixed ${fixedCount} violation(s) — text-white → text-{semantic}-content.\n`);
    } else {
      console.log('✅ No contrast violations found.\n');
    }
  } else {
    console.log(`❌ ${violationCount} contrast violation(s) found in ${violationCount > 0 ? 'source files' : 'source'}.`);
    console.log('   Run `node scripts/lint-contrast.mjs --fix` to auto-replace.\n');
  }

  process.exit(exitCode);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
