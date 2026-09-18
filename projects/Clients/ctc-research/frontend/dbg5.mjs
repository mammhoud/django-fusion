import { chromium } from 'playwright';
const browser = await chromium.launch();
const ctx = await browser.newContext();
const page = await ctx.newPage();
await page.goto('https://ctc-research.com/contact/?lang=ar', { waitUntil: 'networkidle', timeout: 45000 });
await page.waitForTimeout(1500);
for (const name of ['a', 's']) {
  const out = await page.evaluate(async (fn) => {
    const mod = await import('/_astro/runtime-locale.DYtbWPQ5.js');
    try {
      const r = await mod[fn]('en');
      const title = document.querySelector('[data-l10n="contact.title"]')?.textContent;
      const ft = document.querySelector('[data-l10n="contact.form_title"]')?.textContent;
      return { fn, returned: String(r), title, ft };
    } catch (e) {
      return { fn, error: String(e) };
    }
  }, name);
  console.log(JSON.stringify(out));
}
await browser.close();