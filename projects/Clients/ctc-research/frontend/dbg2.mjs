import { chromium } from 'playwright';
const browser = await chromium.launch();
for (const lang of ['en', 'ar', 'sv']) {
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  await page.goto(`https://ctc-research.com/contact/?lang=${lang}`, { waitUntil: 'networkidle', timeout: 45000 }).catch((e) => console.log('goto', String(e)));
  await page.waitForTimeout(2500);
  const form = await page.locator('form').first().innerText().catch(() => 'FORM-MISSING');
  console.log(`=== ${lang} errors=${errors.length} ===`);
  console.log(form.slice(0, 500).replace(/\n+/g, ' | '));
  await ctx.close();
}
await browser.close();