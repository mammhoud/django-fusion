#!/usr/bin/env node
/**
 * Render every ```mermaid block under docs/agenda/ to an SVG image and insert
 * an image reference line right after each block.
 *
 * - Images land in docs/public/agenda/diagrams/<slug>.svg and are served at
 *   /agenda/diagrams/<slug>.svg.
 * - Slug = sanitized relative path of the md file + block index.
 * - Renders via the mermaid.ink SVG API (GET /svg/<base64>).
 * - Idempotent: skips blocks whose image reference line is already present.
 *
 * Usage: node docs/scripts/render-agenda-diagrams.mjs [--render-only]
 *   --render-only  render SVGs but do not edit the markdown files
 */
import { readdir, readFile, writeFile, mkdir, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const agendaRoot = path.join(root, 'agenda');
const outDir = path.join(root, 'public', 'agenda', 'diagrams');
const renderOnly = process.argv.includes('--render-only');
const MERMAID_HEAD = '```mermaid';
// Template placeholder blocks (not real diagrams) are skipped.
const PLACEHOLDER = /\[graph[^\]]*\]|\[nodes and edges[^\]]*\]|\[Feature\/Project|\[sequenceDiagram[^\]]*\]|\[stateDiagram[^\]]*\]|\[erDiagram[^\]]*\]/;

async function walk(dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) files.push(...(await walk(full)));
    else if (entry.isFile() && entry.name.endsWith('.md')) files.push(full);
  }
  return files;
}

function slugFor(relative, index) {
  return relative.replace(/\.md$/i, '').replace(/[^a-zA-Z0-9_-]/g, '-') + `-${index}.svg`;
}

function extractBlocks(source) {
  const blocks = [];
  const lines = source.split('\n');
  let inBlock = false;
  let buf = [];
  let startLine = -1;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!inBlock && line.trim() === MERMAID_HEAD) {
      inBlock = true;
      buf = [];
      startLine = i;
    } else if (inBlock && line.trim() === '```') {
      inBlock = false;
      blocks.push({ code: buf.join('\n'), startLine, endLine: i });
    } else if (inBlock) {
      buf.push(line);
    }
  }
  return blocks;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function render(code, attempts = 4) {
  // base64url — standard base64 can contain '+' and '/' which break URL paths
  const b64 = Buffer.from(code, 'utf8')
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
  const url = `https://mermaid.ink/svg/${b64}`;
  for (let attempt = 1; attempt <= attempts; attempt++) {
    try {
      const res = await fetch(url);
      if (res.status === 503 || res.status === 429 || res.status === 502 || res.status === 404) {
        // rate limited / transient — wait and retry
        await sleep(1200 * attempt);
        continue;
      }
      if (!res.ok) throw new Error(`mermaid.ink ${res.status} for diagram`);
      return await res.text();
    } catch (err) {
      if (attempt === attempts) throw err;
      await sleep(600 * attempt);
    }
  }
  throw new Error('render exhausted retries');
}

let rendered = 0;
let skipped = 0;
let failed = 0;

for (const file of await walk(agendaRoot)) {
  const relative = path.relative(agendaRoot, file);
  const source = await readFile(file, 'utf8');
  const blocks = extractBlocks(source);
  if (!blocks.length) continue;
  let out = source;
  // process from bottom so earlier line offsets stay valid
  for (let i = blocks.length - 1; i >= 0; i--) {
    // be polite to the public render API
    await sleep(250);
    const block = blocks[i];
    if (PLACEHOLDER.test(block.code)) continue;
    const slug = slugFor(relative, i + 1);
    const imgLine = `\n![Rendered diagram](/agenda/diagrams/${slug})`;
    // already referenced? skip
    if (out.includes(`/agenda/diagrams/${slug}`)) {
      skipped++;
      continue;
    }
    let svg;
    try {
      svg = await render(block.code);
    } catch (err) {
      console.error(`✗ ${relative} #${i + 1}: ${err.message}`);
      failed++;
      continue;
    }
    const target = path.join(outDir, slug);
    await mkdir(path.dirname(target), { recursive: true });
    await writeFile(target, svg);
    rendered++;
    if (!renderOnly) {
      // insert after the closing fence (block.endLine is the fence index)
      const lines = out.split('\n');
      lines.splice(block.endLine + 1, 0, imgLine.trimStart());
      out = lines.join('\n');
    }
  }
  if (out !== source) await writeFile(file, out);
}

console.log(
  `Agenda diagrams: ${rendered} rendered, ${skipped} skipped (already referenced), ${failed} failed.`,
);
if (renderOnly) console.log('--render-only: markdown files left untouched.');