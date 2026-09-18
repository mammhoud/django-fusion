import { chromium } from 'playwright';
const browser = await chromium.launch();
const ctx = await browser.newContext();
const page = await ctx.newPage();
await page.goto('https://ctc-research.com/contact/?lang=ar', { waitUntil: 'networkidle', timeout: 45000 });
await page.waitForTimeout(1500);
const before = await page.evaluate(() => document.querySelector('[data-l10n="contact.form_title"]')?.textContent);
const out = await page.evaluate(async () => {
  const mod = await import('/_astro/runtime-locale.DYtbWPQ5.js');
  await mod.a();
  return {
    title: document.querySelector('[data-l10n="contact.title"]')?.textContent,
    ft: document.querySelector('[data-l10n="contact.form_title"]')?.textContent,
    label: document.querySelector('[data-l10n="contact.field.name.label"]')?.textContent,
    btn: document.querySelector('[data-l10n="contact.button_text"]')?.textContent,
    lang: document.documentElement.lang,
  };
});
console.log('before:', before);
console.log('after :', JSON.stringify(out));
await browser.close();