/**
 * Live smoke test — runs against the DEPLOYED tools-web container
 * through tools-proxy (no webServer fixture). Requires the stack to be up:
 *   docker compose -f application/tools/docker-compose.nginx.yml up -d tools-proxy
 *   docker compose -f application/tools/docker-compose.yml up -d tools-web
 */
import { chromium } from '@playwright/test';

const BASE = process.env.TOOLS_SMOKE_URL || 'http://127.0.0.1:4321';
// Must match the deployed TOOLS_UNLOCK_PASSWORD; no default baked in.
const UNLOCK = process.env.TOOLS_UNLOCK_PASSWORD;
if (!UNLOCK) {
  console.error('Set TOOLS_UNLOCK_PASSWORD to run the live smoke test');
  process.exit(2);
}

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
let failed = 0;

async function check(name, fn) {
  try {
    await fn();
    console.log(`  ✓ ${name}`);
  } catch (e) {
    failed += 1;
    console.log(`  ✘ ${name}: ${String(e.message).split('\n')[0]}`);
  }
}

await check('dashboard serves sign-in modal', async () => {
  await page.goto(`${BASE}/`);
  await page.getByRole('heading', { name: 'Sign in' }).waitFor({ timeout: 8000 });
});

await check('sign in with admin/admin', async () => {
  await page.getByLabel('Username').fill('admin');
  await page.getByLabel('Password', { exact: true }).fill('admin');
  await page.getByRole('button', { name: 'Sign In' }).click();
  await page.getByRole('heading', { name: /Application/ }).waitFor({ timeout: 8000 });
});

await check('tool card opens unlock modal', async () => {
  await page.locator('.card', { hasText: 'Blinko' }).click();
  await page.getByRole('heading', { name: 'Open Blinko' }).waitFor({ timeout: 5000 });
});

await check('wrong unlock password rejected', async () => {
  await page.getByLabel('Unlock password').fill('nope');
  await page.getByRole('button', { name: 'Open tool' }).click();
  await page.getByText('Incorrect password for this tool').waitFor({ timeout: 5000 });
});

await check('correct unlock navigates to /notes/', async () => {
  await page.getByLabel('Unlock password').fill(UNLOCK);
  await page.getByRole('button', { name: 'Open tool' }).click();
  await page.waitForURL('**/notes/', { timeout: 8000 });
});

await check('theme toggle flips to dark', async () => {
  await page.goto(`${BASE}/`);
  await page.getByRole('heading', { name: /Application/ }).waitFor({ timeout: 8000 });
  await page.locator('.theme-toggle').click();
  const cls = await page.locator('html').getAttribute('class');
  if (!/dark/.test(cls || '')) throw new Error('html did not get .dark');
});

await browser.close();
console.log(failed ? `\n${failed} check(s) FAILED` : '\nAll live checks passed');
process.exit(failed ? 1 : 0);
