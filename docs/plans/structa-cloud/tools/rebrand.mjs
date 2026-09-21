#!/usr/bin/env node
/**
 * rebrand.mjs — Structa Cloud marketplace rebrand + publish gate
 * ─────────────────────────────────────────────────────────────────────
 * Owning plan: docs/plans/structa-cloud/README.md
 * Source of truth: tools/rebrand-map.json (edit that, not this file)
 *
 * TWO JOBS, never mixed:
 *   1. rebrand — apply identity replacements to surfaces marked
 *      `rebrandable: true`. Files on any other surface are never written,
 *      no matter what the map says.
 *   2. gate    — scan publish-set surfaces for denylist violations
 *      (third-party attribution, retired names, placeholder media, …).
 *
 * Usage:
 *   node rebrand.mjs                 # check (default) — read-only, exit 1 on findings
 *   node rebrand.mjs --check         # same as default
 *   node rebrand.mjs --apply         # write replacements to rebrandable surfaces
 *   node rebrand.mjs --surface X     # limit to one surface id
 *   node rebrand.mjs --list          # list surfaces and their gates
 *   node rebrand.mjs --json          # machine-readable report
 *   node rebrand.mjs --quiet         # summary only
 *
 * This tool never uploads, prices, or submits anything to a marketplace.
 * Publishing stays an operator action (see the plan's "Effectful" section).
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(HERE, '..', '..', '..', '..');

const argv = process.argv.slice(2);
const has = (flag) => argv.includes(flag);
const valueOf = (name) => {
  const eq = argv.find((a) => a.startsWith(`${name}=`));
  if (eq) return eq.slice(name.length + 1);
  const i = argv.indexOf(name);
  return i !== -1 ? argv[i + 1] : undefined;
};

const MODE = has('--apply') ? 'apply' : 'check';
const AS_JSON = has('--json');
const QUIET = has('--quiet');
const ONLY = valueOf('--surface');
const FORCE = has('--force'); // allow writing inside neverWrite paths (not advised)

/* ── map ────────────────────────────────────────────────────────────── */

const mapPath = path.join(HERE, 'rebrand-map.json');
if (!fs.existsSync(mapPath)) fail(`missing map: ${path.relative(REPO_ROOT, mapPath)}`);
const map = JSON.parse(fs.readFileSync(mapPath, 'utf8'));

/* ── helpers ────────────────────────────────────────────────────────── */

function fail(message) {
  console.error(`\n✖ ${message}\n`);
  process.exit(2);
}

function toPosix(p) {
  return p.split(path.sep).join('/');
}

function rel(abs) {
  return toPosix(path.relative(REPO_ROOT, abs));
}

/** Compile a map rule into a global RegExp. Handles the `(?i)` prefix that
 *  ripgrep accepts and JavaScript does not. */
function compile(rule) {
  if (rule.kind === 'literal') {
    return { regex: null, literal: rule.pattern, replace: rule.replace };
  }
  let source = rule.pattern;
  let flags = 'g';
  if (source.startsWith('(?i)')) {
    source = source.slice(4);
    flags += 'i';
  }
  return { regex: new RegExp(source, flags), literal: null, replace: rule.replace };
}

function countMatches(text, compiled) {
  if (compiled.literal !== null) {
    if (compiled.literal === '') return 0;
    return text.split(compiled.literal).length - 1;
  }
  return (text.match(compiled.regex) || []).length;
}

function applyRule(text, compiled) {
  if (compiled.literal !== null) return text.split(compiled.literal).join(compiled.replace);
  return text.replace(compiled.regex, compiled.replace);
}

const EXCLUDE = new Set(map.excludeDirs || []);
const TEXT_EXT = new Set(map.textExtensions || []);

/** Walk a surface root (file or dir) collecting text files. */
function collectFiles(rootRel) {
  const abs = path.join(REPO_ROOT, rootRel);
  if (!fs.existsSync(abs)) return { files: [], missing: true };

  const out = [];
  const walk = (dir) => {
    let entries;
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      if (EXCLUDE.has(entry.name)) continue;
      const child = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(child);
      else if (entry.isFile() && TEXT_EXT.has(path.extname(entry.name))) out.push(child);
    }
  };

  const stat = fs.statSync(abs);
  if (stat.isFile()) return { files: [abs], missing: false };
  walk(abs);
  return { files: out, missing: false };
}

function isNeverWritable(abs) {
  const r = rel(abs);
  return (map.neverWrite || []).some((p) => r === p || r.startsWith(`${p}/`));
}

/* ── --list ─────────────────────────────────────────────────────────── */

if (has('--list')) {
  const rows = (map.surfaces || []).map((s) => {
    const gate =
      s.licence === 'third-party'
        ? 'third-party — excluded from publish'
        : s.rebrandable
          ? 'rebrandable'
          : `read-only${s.blockedBy ? ` (${s.blockedBy})` : ''}`;
    return `  ${s.id.padEnd(24)} ${gate.padEnd(38)} ${s.roots.length} root(s)`;
  });
  console.log(['', `Structa Cloud rebrand surfaces — ${map.product.canonicalName}`, '', ...rows, ''].join('\n'));
  process.exit(0);
}

/* ── report scaffold ────────────────────────────────────────────────── */

const report = {
  mode: MODE,
  repoRoot: REPO_ROOT,
  surfaces: [],
  findings: { replacementsPending: 0, replacementsApplied: 0, denylistHits: 0, missingRoots: 0 },
};

const surfaces = (map.surfaces || []).filter((s) => !ONLY || s.id === ONLY);
if (surfaces.length === 0) fail(`no surface matched${ONLY ? ` --surface ${ONLY}` : ''}`);

/* ── per-surface work ───────────────────────────────────────────────── */

for (const surface of surfaces) {
  const rules = (map.replacements || []).filter((r) => r.surface === surface.id).map((r) => ({
    ...r,
    compiled: compile(r),
  }));

  const files = [];
  let missingRoots = 0;
  for (const root of surface.roots) {
    const { files: found, missing } = collectFiles(root);
    if (missing) missingRoots += 1;
    files.push(...found);
  }
  report.findings.missingRoots += missingRoots;

  const entry = {
    id: surface.id,
    label: surface.label,
    licence: surface.licence,
    rebrandable: !!surface.rebrandable,
    publishSet: !!surface.publishSet,
    blockedBy: surface.blockedBy || null,
    note: surface.note || null,
    filesScanned: files.length,
    missingRoots,
    replacements: { pending: [], applied: [], alreadyDone: 0 },
    denylist: [],
    refused: [],
  };

  for (const abs of files) {
    let text;
    try {
      text = fs.readFileSync(abs, 'utf8');
    } catch {
      continue;
    }
    const fileRel = rel(abs);

    /* 1. rebrand replacements — rebrandable surfaces only */
    if (surface.rebrandable) {
      for (const rule of rules) {
        const hits = countMatches(text, rule.compiled);
        const done = countMatches(text, compile({ ...rule, kind: 'literal', pattern: rule.replace }));
        if (hits === 0) {
          if (done > 0) entry.replacements.alreadyDone += 1;
          continue;
        }
        if (isNeverWritable(abs) && !FORCE) {
          entry.refused.push({ file: fileRel, rule: rule.id, reason: 'inside neverWrite' });
          continue;
        }
        entry.replacements.pending.push({ file: fileRel, rule: rule.id, hits });

        if (MODE === 'apply') {
          const next = applyRule(text, rule.compiled);
          fs.writeFileSync(abs, next, 'utf8');
          text = next;
          entry.replacements.applied.push({ file: fileRel, rule: rule.id, hits });
        }
      }
    }

    /* 2. publish gate — publish-set surfaces only */
    if (surface.publishSet) {
      for (const rule of map.denylist || []) {
        const compiled = compile({ ...rule, replace: '' });
        const hits = countMatches(text, compiled);
        if (hits > 0) entry.denylist.push({ file: fileRel, rule: rule.id, label: rule.label, hits, reason: rule.reason });
      }
    }
  }

  report.findings.replacementsPending += entry.replacements.pending.length;
  report.findings.replacementsApplied += entry.replacements.applied.length;
  report.findings.denylistHits += entry.denylist.length;
  report.surfaces.push(entry);
}

/* ── output ─────────────────────────────────────────────────────────── */

if (AS_JSON) {
  console.log(JSON.stringify(report, null, 2));
} else {
  printHuman(report);
}

const blocking =
  (MODE === 'check' && report.findings.replacementsPending > 0) ||
  report.findings.denylistHits > 0 ||
  report.surfaces.some((s) => s.refused.length > 0);

process.exit(blocking ? 1 : 0);

/* ── printing ───────────────────────────────────────────────────────── */

function printHuman(rep) {
  const out = [];
  out.push('');
  out.push(`Structa Cloud rebrand — ${rep.mode === 'apply' ? 'APPLY' : 'CHECK (read-only)'}`);
  out.push(`repo: ${rep.repoRoot}`);
  out.push('');

  for (const s of rep.surfaces) {
    const gate =
      s.licence === 'third-party'
        ? 'third-party — excluded from any publish set'
        : s.rebrandable
          ? 'rebrandable'
          : s.blockedBy
            ? `read-only — blocked by ${s.blockedBy}`
            : 'read-only';
    out.push(`── ${s.id} — ${s.label}`);
    out.push(`   licence: ${s.licence} · ${gate} · ${s.filesScanned} file(s) scanned`);
    if (s.note && !QUIET) out.push(`   note: ${s.note}`);

    if (s.missingRoots > 0) out.push(`   ⚠ ${s.missingRoots} declared root(s) do not exist in this checkout`);

    if (s.replacements.pending.length) {
      out.push(`   replacements pending: ${s.replacements.pending.length}`);
      if (!QUIET) {
        for (const p of s.replacements.pending) out.push(`     · ${p.rule}  ${p.file}  (${p.hits})`);
      }
    }
    if (s.replacements.applied.length) out.push(`   replacements applied: ${s.replacements.applied.length}`);
    if (s.replacements.alreadyDone > 0 && !QUIET) out.push(`   already rebranded: ${s.replacements.alreadyDone}`);

    if (s.denylist.length) {
      out.push(`   ✖ publish-gate violations: ${s.denylist.length}`);
      for (const d of s.denylist) {
        out.push(`     · [${d.rule}] ${d.label} — ${d.file} (${d.hits})`);
        if (!QUIET) out.push(`       ${d.reason}`);
      }
    }
    if (s.refused.length) {
      out.push(`   ✖ refused writes: ${s.refused.length}`);
      for (const r of s.refused) out.push(`     · ${r.rule}  ${r.file}  (${r.reason})`);
    }
    out.push('');
  }

  const f = rep.findings;
  out.push('Summary');
  out.push(`  replacements pending : ${f.replacementsPending}`);
  out.push(`  replacements applied : ${f.replacementsApplied}`);
  out.push(`  publish-gate hits    : ${f.denylistHits}`);
  out.push(`  missing roots        : ${f.missingRoots}`);
  out.push('');
  if (rep.mode === 'check') {
    out.push(
      f.replacementsPending === 0 && f.denylistHits === 0
        ? '✔ clean — nothing pending, no publish-gate violations'
        : '✖ findings above — run with --apply to rebrand, then resolve gate hits by hand',
    );
  } else {
    out.push('✔ apply complete — re-run with --check to confirm');
  }
  out.push('');

  console.log(out.join('\n'));
}
