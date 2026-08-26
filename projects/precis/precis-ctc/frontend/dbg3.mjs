import { chromium } from 'playwright';
const browser = await chromium.launch();
const ctx = await browser.newContext();
const page = await ctx.newPage();
const errors = [];
page.on('pageerror', (e) => errors.push(String(e)));
await page.goto('https://ctc-research.com/contact/?lang=ar', { waitUntil: 'networkidle', timeout: 45000 });
await page.waitForTimeout(2000);
const probe = await page.evaluate(async () => {
  const resp = await fetch('/apis/contact/?lang=ar&locale_refresh=1', { cache: 'no-store' });
  const data = await resp.json().catch(() => null);
  const nodes = [...document.querySelectorAll('[data-l10n]')].map((n) => ({
    key: n.getAttribute('data-l10n'),
    tag: n.tagName,
    text: (n.textContent || '').slice(0, 40),
  }));
  return { ok: resp.ok, language: data?.language, form_title: data?.form_title, nodes: nodes.slice(0, 12) };
});
console.log('errors:', errors);
console.log(JSON.stringify(probe, null, 1));
await browser.close();