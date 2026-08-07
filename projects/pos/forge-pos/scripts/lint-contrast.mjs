#!/usr/bin/env node

/**
 * lint-contrast.mjs
 *
 * Two checks over src/*.ts and src/*.tsx (excluding tests):
 *
 * 1. Tailwind class check: `bg-{semantic} text-white` patterns that should use
 *    `text-{semantic}-content` instead for theme-aware contrast.
 * 2. Hardcoded text-color check: jsPDF-style `setTextColor(...)` calls and
 *    `textColor = ...` assignments whose color fails WCAG AA (4.5:1) contrast
 *    against the effective background (last `setFillColor(...)`, white by
 *    default). Light text on a dark fill (e.g. white on a teal badge) passes
 *    at the 3:1 large-text/UI threshold.
 *
 * Usage: node scripts/lint-contrast.mjs [--fix]
 *
 * Without --fix: reports violations with file:line:col format.
 * With --fix:    auto-replaces `text-white` with `text-{semantic}-content`.
 *                Hardcoded text-color violations are only reported — the
 *                replacement color is a design decision, so fix them manually
 *                (or suppress with a `lint-disable-line` comment on the line).
 *
 * Exit code: 0 if clean, 1 if violations found.
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
const AA_NORMAL = 4.5; // WCAG AA normal-size text
const AA_LARGE = 3.0; // WCAG AA large text / UI components
const WHITE = [255, 255, 255];

// A setFillColor only counts as the text background when it is set close to
// the text (jsPDF badge pattern: fill → draw → text within a few statements).
// Fills from earlier in the file (e.g. a header strip) don't sit behind text
// drawn later on the white page, so they must not affect the contrast check.
const FILL_WINDOW_LINES = 6;

let exitCode = 0;
let fixedCount = 0;
let violationCount = 0;
let hexViolationCount = 0;

/** Walk a directory tree and collect .ts / .tsx file paths (excluding tests). */
function collectSourceFiles(dir) {
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
      results.push(...collectSourceFiles(fullPath));
    } else if (
      entry.isFile() &&
      (extname(entry.name) === '.tsx' || extname(entry.name) === '.ts') &&
      !entry.name.endsWith('.test.tsx') &&
      !entry.name.endsWith('.spec.tsx') &&
      !entry.name.endsWith('.test.ts') &&
      !entry.name.endsWith('.spec.ts')
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

// ── WCAG contrast helpers ────────────────────────────────────────────

/** Convert a #rgb / #rrggbb / #rrggbbaa hex (or 0xrrggbb) to [r,g,b]. */
function hexToRgb(hex) {
  let h = hex.replace(/^#/, '');
  if (/^0x/i.test(h)) h = h.slice(2);
  if (h.length === 3) h = [...h].map((c) => c + c).join('');
  if (h.length === 8) h = h.slice(0, 6); // drop alpha
  if (!/^[0-9a-fA-F]{6}$/.test(h)) return null;
  return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
}

/**
 * Parse a color argument list (whitespace + quotes stripped).
 * Accepts `r,g,b`, `r,g,b,a`, `rgb(r,g,b)`, `#rrggbb`, `#rgb`, `0xrrggbb`.
 * Returns [r,g,b] or null when the expression isn't a literal color.
 */
function parseColor(args) {
  const s = args.replace(/['"\s]/g, '').toLowerCase();
  if (!s) return null;

  const hex = s.match(/^(?:#|0x)([0-9a-f]{3,8})$/);
  if (hex) return hexToRgb(hex[1]);

  const rgb = s.match(/^(?:rgba?\(|)(\d{1,3}),(\d{1,3}),(\d{1,3})(?:,\d+(?:\.\d+)?)?\)?$/);
  if (rgb) return [parseInt(rgb[1], 10), parseInt(rgb[2], 10), parseInt(rgb[3], 10)];

  return null;
}

/** WCAG relative luminance of an [r,g,b] triplet. */
function luminance([r, g, b]) {
  const chan = [r, g, b].map((v) => {
    const c = v / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * chan[0] + 0.7152 * chan[1] + 0.0722 * chan[2];
}

/** WCAG contrast ratio between two [r,g,b] triplets (1..21). */
function contrastRatio(a, b) {
  const la = luminance(a);
  const lb = luminance(b);
  const [hi, lo] = la > lb ? [la, lb] : [lb, la];
  return (hi + 0.05) / (lo + 0.05);
}

/** Map a byte offset into a content string to a 1-based line number. */
function lineAt(content, offset) {
  let line = 1;
  for (let i = 0; i < offset && i < content.length; i++) {
    if (content[i] === '\n') line++;
  }
  return line;
}

/** Collect every text-color occurrence with its start/end line numbers. */
function findTextColors(content) {
  const found = [];
  const callRe = /setTextColor\s*\(([\s\S]*?)\)/g;
  const assignRe = /textColor\s*=\s*([^;\n]+)/g;
  for (const [re, groupIdx] of [[callRe, 1], [assignRe, 1]]) {
    let m;
    while ((m = re.exec(content)) !== null) {
      const start = m.index;
      const end = re.lastIndex;
      found.push({
        args: m[groupIdx],
        startLine: lineAt(content, start),
        endLine: lineAt(content, end),
      });
    }
  }
  return found;
}

/** Collect every setFillColor occurrence (multi-line aware) with start line. */
function findFills(content) {
  const found = [];
  const re = /setFillColor\s*\(([\s\S]*?)\)/g;
  let m;
  while ((m = re.exec(content)) !== null) {
    found.push({
      args: m[1],
      line: lineAt(content, m.index),
      color: parseColor(m[1]),
    });
  }
  return found;
}

/** The line text covering an occurrence (for lint-disable-line detection). */
function occurrenceLines(content, occurrence) {
  return content.split('\n').slice(occurrence.startLine - 1, occurrence.endLine);
}

/**
 * Check a file for hardcoded text colors failing WCAG AA.
 * Reports violations as it goes.
 */
function checkHardcodedTextColors(file, content, relative) {
  const textColors = findTextColors(content);
  if (!textColors.length) return;

  const fills = findFills(content);

  for (const tc of textColors) {
    const color = parseColor(tc.args);
    // Non-literal argument (variable, ternary, expression) — not a hardcoded color.
    if (!color) continue;

    const textIsLight = luminance(color) > 0.5;

    // Background resolution:
    //  - Light text (white-on-badge pattern) is checked against the most recent
    //    fill set in the adjacent window; with no fill it sits on the white page.
    //  - Dark text is body text on the white page — the fill belongs to a
    //    separate drawn region, so it always checks against white.
    let bgColor = WHITE;
    let unknownBg = false;
    if (textIsLight) {
      const fill = fills
        .filter((f) => f.line <= tc.startLine && tc.startLine - f.line <= FILL_WINDOW_LINES)
        .pop();
      if (fill?.color) bgColor = fill.color;
      else if (fill) unknownBg = true; // unparseable fill expression
    }

    const ratio = contrastRatio(color, bgColor);
    const bgIsDark = bgColor === WHITE ? false : luminance(bgColor) < 0.4;

    // Light text on a dark fill (badge / header) — OK at the 3:1 UI threshold.
    const badgeExempt =
      textIsLight && bgIsDark && ratio >= AA_LARGE && ratio < AA_NORMAL;

    // Unknown background (unparseable fill expression) — can't prove a
    // violation, so only flag when the text is dark (i.e. definitely on white).
    if (unknownBg && textIsLight) continue;

    if (ratio >= AA_NORMAL || badgeExempt) continue;

    // Repo convention: `lint-disable-line` inline allowlist.
    if (occurrenceLines(content, tc).some((l) => l.includes('lint-disable-line'))) continue;

    exitCode = 1;
    hexViolationCount++;
    const firstLine = occurrenceLines(content, tc)[0] || '';
    const col = (firstLine.indexOf('setTextColor') + 1) || (firstLine.indexOf('textColor') + 1) || 1;
    const snippet = firstLine.trim().substring(0, 80).replace(/\s+/g, ' ') || '';
    const fixHint =
      textIsLight && bgColor === WHITE
        ? `white text on white/light bg (${ratio.toFixed(2)}:1) — use a dark text color or add lint-disable-line`
        : `contrast ${ratio.toFixed(2)}:1 on ${bgColor === WHITE ? 'white' : `#${bgColor.map((v) => v.toString(16).padStart(2, '0')).join('')}`} — need ≥ ${AA_NORMAL}:1, or add lint-disable-line`;

    console.log(`  ✗ ${relative}:${tc.startLine}:${col}`);
    console.log(`     ${snippet}`);
    console.log(`     → ${fixHint}`);
    console.log('');
  }
}

async function main() {
  const srcDir = join(ROOT_DIR, 'src');
  const files = collectSourceFiles(srcDir);

  console.log(`\n🔍 Scanning ${files.length} .ts/.tsx files for contrast violations...\n`);

  for (const file of files) {
    const content = readFileSync(file, 'utf-8');
    const lines = content.split('\n');
    const relative = file.replace(ROOT_DIR + '/', '');
    let fileModified = false;

    // ── Check 1: bg-{semantic} text-white Tailwind pattern ──
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

    // ── Check 2: hardcoded text colors failing WCAG AA ──
    checkHardcodedTextColors(file, content, relative);

    if (FIX && fileModified) {
      writeFileSync(file, lines.join('\n'), 'utf-8');
    }
  }

  if (exitCode === 0) {
    if (FIX && fixedCount > 0) {
      console.log(`✅ Fixed ${fixedCount} text-white violation(s) → text-{semantic}-content.\n`);
    } else {
      console.log('✅ No contrast violations found.\n');
    }
  } else {
    if (violationCount > 0) {
      console.log(`❌ ${violationCount} text-white contrast violation(s) found.`);
      console.log('   Run `node scripts/lint-contrast.mjs --fix` to auto-replace.\n');
    }
    if (hexViolationCount > 0) {
      console.log(`❌ ${hexViolationCount} hardcoded text-color violation(s) found.`);
      console.log('   Replace the color manually (design decision) or add `// lint-disable-line`.\n');
    }
  }

  process.exit(exitCode);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
