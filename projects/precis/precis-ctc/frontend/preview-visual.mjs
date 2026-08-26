/**
 * CTC Research — visual preview + runtime audit (Playwright).
 *
 * Visits the public pages (default https://ctc-research.com, override with
 * BASE_URL), collects console errors / failed requests / broken images, and
 * saves full-page screenshots + a gallery HTML so a human can review the
 * live design and translations.
 *
 * Usage:  node preview-visual.mjs [BASE_URL] [OUT_DIR]
 */
import { chromium } from '@playwright/test';
import { mkdirSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const BASE_URL = process.argv[2] || 'https://ctc-research.com';
const OUT_DIR = path.resolve(process.argv[3] || '/tmp/ctc-preview');
const SHOTS = path.join(OUT_DIR, 'shots');
mkdirSync(SHOTS, { recursive: true });

const PAGES = [
  { name: 'home', url: '/' },
  { name: 'home-ar', url: '/?lang=ar' },
  { name: 'home-de', url: '/?lang=de' },
  { name: 'courses', url: '/courses/' },
  { name: 'courses-fr', url: '/courses/?lang=fr' },
  { name: 'course-detail', url: '/courses/clinical-trial-design-protocol-development/' },
  { name: 'about', url: '/about/' },
  { name: 'about-ar', url: '/about/?lang=ar' },
  { name: 'events', url: '/events/' },
  { name: 'team', url: '/team/' },
  { name: 'contact', url: '/contact/' },
  { name: 'services', url: '/services/' },
];

const results = [];
let browser;

try {
  browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  for (const item of PAGES) {
    const log = { name: item.name, url: item.url, http: 0, consoleErrors: [], pageErrors: [], failed: [], brokenImages: [] };
    page.on('console', (msg) => {
      if (msg.type() === 'error') log.consoleErrors.push(msg.text().slice(0, 200));
    });
    page.on('pageerror', (err) => log.pageErrors.push(String(err).slice(0, 200)));
    page.on('requestfailed', (req) => {
      if (!req.url().includes('favicon')) log.failed.push(`${req.url().slice(0, 120)} -> ${req.failure()?.errorText || ''}`);
    });

    try {
      const response = await page.goto(BASE_URL + item.url, { waitUntil: 'networkidle', timeout: 60_000 });
      log.http = response?.status() ?? 0;
      // Let reveal/GSAP animations and the ?lang= hydration finish.
      await page.waitForTimeout(1800);
      // Scroll through the page to trigger reveal animations, then settle.
      await page.evaluate(async () => {
        const step = 600;
        for (let y = 0; y <= document.body.scrollHeight; y += step) {
          window.scrollTo(0, y);
          await new Promise((r) => setTimeout(r, 90));
        }
        window.scrollTo(0, 0);
      });
      await page.waitForTimeout(900);

      // Broken images: any <img> that failed to decode/load.
      const broken = await page.evaluate(() =>
        [...document.querySelectorAll('img')]
          .filter((img) => img.complete && img.naturalWidth === 0)
          .map((img) => img.getAttribute('src') || img.src || '(inline)')
          .slice(0, 12),
      );
      log.brokenImages = broken;

      await page.screenshot({ path: path.join(SHOTS, `${item.name}.png`), fullPage: true });
    } catch (err) {
      log.pageErrors.push(`NAVIGATION: ${String(err).slice(0, 200)}`);
    }
    results.push(log);
    console.log(JSON.stringify(log));
  }

  await browser.close();
} catch (err) {
  console.error('Preview failed:', err);
  if (browser) await browser.close();
  process.exitCode = 1;
}

// ── Gallery page ────────────────────────────────────────────────────────────
const cards = results.map((r) => {
  const errors = [...r.consoleErrors, ...r.pageErrors, ...r.failed, ...r.brokenImages.map((i) => `broken image: ${i}`)];
  const badge = r.http >= 400 ? 'HTTP ' + r.http : r.http || 'n/a';
  const ok = r.http >= 200 && r.http < 400 && errors.length === 0;
  return `<div class="card ${ok ? 'ok' : 'bad'}">
    <h2>${r.name} <span class="http">${badge}</span> <span class="status">${ok ? '✅' : '⚠️'}</span></h2>
    <p class="url">${BASE_URL}${r.url}</p>
    <a href="shots/${r.name}.png"><img src="shots/${r.name}.png" alt="${r.name}" loading="lazy"></a>
    ${errors.length ? `<details><summary>${errors.length} issue(s)</summary><ul>${errors.map((e) => `<li>${escapeHtml(e)}</li>`).join('')}</ul></details>` : '<p class="clean">No console/page/network/image errors.</p>'}
  </article>`;
}).join('');

function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

writeFileSync(path.join(OUT_DIR, 'index.html'), `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CTC Research — visual preview</title>
<style>
  body { font-family: system-ui, sans-serif; background: #f4f4f0; color: #0a0a0a; margin: 0; padding: 2rem; }
  header h1 { font-size: 1.6rem; margin: 0 0 .25rem; }
  header p { color: #666; margin: 0 0 1.5rem; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 1.25rem; }
  .card { background: #fff; border: 2px solid #0a0a0a; padding: 1rem; }
  .card.bad { border-color: #e61919; }
  .card h2 { font-size: 1rem; margin: 0 0 .25rem; display: flex; gap: .5rem; align-items: center; }
  .badge { font: 700 .7rem/1.4 ui-monospace, monospace; border: 1px solid #999; padding: .1rem .4rem; }
  .url { font-size: .75rem; color: #666; margin: 0 0 .75rem; }
  .card img { width: 100%; border: 1px solid #ddd; }
  details { margin-top: .75rem; font-size: .8rem; }
  details summary { cursor: pointer; font-weight: 600; }
  ul { margin: .5rem 0; padding-left: 1.1rem; }
  li { margin: .2rem 0; }
  .clean { font-size: .8rem; color: #1a7a3a; margin-top: .75rem; }
</style></head>
<body>
<header><h1>CTC Research — visual preview</h1>
<p>Generated ${new Date().toISOString()} · ${BASE_URL} · ${results.length} pages · click to open the full-size screenshot</p></header>
<div class="grid">${cards}</div>
</body></html>`);

console.log(`Gallery: file://${path.join(OUT_DIR, 'index.html')}`);