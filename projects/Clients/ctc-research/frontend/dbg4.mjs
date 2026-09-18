import { chromium } from 'playwright';
const browser = await chromium.launch();
const ctx = await browser.newContext();
const page = await ctx.newPage();
await page.goto('https://ctc-research.com/contact/?lang=ar', { waitUntil: 'networkidle', timeout: 45000 });
await page.waitForTimeout(1500);
const out = await page.evaluate(async () => {
  const mod = await import('/_astro/runtime-locale.DYtbWPQ5.js');
  const names = Object.keys(mod);
  return names;
});
console.log('exported:', out);
await browser.close();