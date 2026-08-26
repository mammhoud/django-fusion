import { chromium } from 'playwright';
const browser = await chromium.launch();
for (const lang of ['en', 'ar']) {
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  await page.goto(`https://ctc-research.com/contact/?lang=${lang}`, { waitUntil: 'networkidle', timeout: 45000 }).catch((e) => console.log('goto err', String(e)));
  await page.waitForTimeout(1500);
  const txt = (await page.locator('body').innerText().catch(() => '')).replace(/\n+/g, ' | ');
  console.log(`=== ${lang} errors=${errors.length}`);
  console.log(txt.slice(0, 600));
  await ctx.close();
}
await browser.close();