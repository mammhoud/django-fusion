import { chromium } from 'playwright';
const browser = await chromium.launch();
const ctx = await browser.newContext();
const page = await ctx.newPage();
await page.addInitScript(() => {
  window.__fetches = [];
  const orig = window.fetch.bind(window);
  window.fetch = async (...args) => {
    const res = await orig(...args);
    if (String(args[0]).includes('/apis/contact')) {
      const body = await res.clone().json().catch(() => null);
      window.__fetches.push({ url: String(args[0]), status: res.status, language: body?.language, form_title: body?.form_title });
    }
    return res;
  };
});
await page.goto('https://ctc-research.com/contact/?lang=ar', { waitUntil: 'networkidle', timeout: 45000 });
await page.waitForTimeout(2500);
const out = await page.evaluate(async () => {
  await (await import('/_astro/runtime-locale.DYtbWPQ5.js')).a();
  return {
    fetches: window.__fetches,
    ft: document.querySelector('[data-l10n="contact.form_title"]')?.textContent,
    lang: document.documentElement.lang,
  };
});
console.log(JSON.stringify(out, null, 1));
await browser.close();