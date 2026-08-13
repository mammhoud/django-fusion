#!/usr/bin/env node
/**
 * Formint Cloud — Capture the design-reference boards as PNGs.
 *
 * Renders docs/mobile_ops_preview.html and docs/desktop_monitor_preview.html
 * in headless Chromium (Playwright, already a frontend devDependency) and
 * writes full-page screenshots to docs/images/ so the README's Design
 * references section can embed them.
 *
 * Captures at 2x DPR for crisp supersampled detail, then post-processes with
 * the backend venv's Pillow: downscales to 1280px wide and palette-quantizes
 * to 256 colors so the committed PNGs stay lean. If Pillow is unavailable,
 * the raw 2x captures are kept and a warning is printed.
 *
 * Usage (from the formint-cloud/ root, or anywhere — @playwright/test resolves
 * against the frontend package):
 *   node scripts/dev/screenshot-boards.mjs
 */

import { mkdirSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..'); // formint-cloud/
// Resolve @playwright/test from the frontend's node_modules (the script
// lives outside any package, so createRequire anchors resolution there).
const require = createRequire(join(ROOT, 'frontend', 'package.json'));
const { chromium } = require('@playwright/test');

const DOCS = join(ROOT, 'docs');
const OUT = join(DOCS, 'images');
mkdirSync(OUT, { recursive: true });

const boards = [
  { file: 'mobile_ops_preview.html', out: 'mobile-ops-preview.png', viewport: { width: 1440, height: 900 } },
  { file: 'desktop_monitor_preview.html', out: 'desktop-monitor-preview.png', viewport: { width: 1440, height: 900 } },
];

const browser = await chromium.launch();
try {
  for (const board of boards) {
    const page = await browser.newPage({ viewport: board.viewport, deviceScaleFactor: 2 });
    await page.goto(`file://${join(DOCS, board.file)}`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(300); // let the grain/scanline textures settle
    const path = join(OUT, board.out);
    await page.screenshot({ path, fullPage: true });
    const size = await page.evaluate(() => ({
      w: document.documentElement.scrollWidth,
      h: document.documentElement.scrollHeight,
    }));
    console.log(`✓ ${board.file} → ${board.out} (${size.w}×${size.h})`);
    await page.close();
  }
} finally {
  await browser.close();
}

// ── Post-process: downscale to 1280px wide + quantize to 256 colors ────────
const pyBin = process.platform === 'win32' ? 'Scripts' : 'bin';
const venvPy = join(ROOT, 'backend', '.venv', pyBin, process.platform === 'win32' ? 'python.exe' : 'python');
const POST_PROCESS = `
from PIL import Image
import sys
for name in sys.argv[1:]:
    img = Image.open(name).convert("RGB")
    w, h = img.size
    if w > 1280:
        img = img.resize((1280, round(h * 1280 / w)), Image.LANCZOS)
    img = img.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG)
    img.save(name, optimize=True)
`;
const paths = boards.map((b) => join(OUT, b.out));
try {
  execFileSync(venvPy, ['-c', POST_PROCESS, ...paths], { stdio: 'inherit' });
  console.log('✓ post-processed: 1280px wide, 256-color palette');
} catch {
  console.warn('⚠ Pillow not found in backend/.venv — raw 2x captures kept. Install Pillow to auto-shrink.');
}
