import { chromium } from 'playwright';
import fs from 'node:fs';

const BASE = 'http://127.0.0.1:1111';
const SHOTS = '/tmp/blinko-walkthrough';
fs.mkdirSync(SHOTS, { recursive: true });

const consoleErrors = [];
const pageErrors = [];
const badResponses = [];
const created = { notes: [] };

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
page.on('console', (msg) => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
page.on('pageerror', (err) => pageErrors.push(String(err)));
page.on('response', (res) => { if (res.status() >= 400) badResponses.push(`${res.status()} ${res.url()}`); });
page.on('dialog', (d) => d.accept());

const step = async (name, fn) => {
  try { await fn(); console.log(`PASS ${name}`); }
  catch (e) { console.log(`FAIL ${name}: ${String(e).split('\n')[0]}`); throw e; }
};

try {
  await step('login', async () => {
    await page.goto(BASE, { waitUntil: 'networkidle' });
    const switchBtn = page.locator('#switch-auth');
    if (await switchBtn.isVisible() && (await switchBtn.textContent()).includes('Sign in')) {
      await switchBtn.click();
    }
    await page.fill('#username', 'superadmin');
    await page.fill('#password', 'admin123');
    await page.click('#auth-form button[type="submit"]');
    await page.waitForSelector('#app-panel:not(.hidden)', { timeout: 15000 });
  });

  /* ---------- KANBAN ---------- */
  await step('open kanban', async () => {
    await page.click('[data-view="kanban"]');
    await page.waitForSelector('.kanban-column', { timeout: 10000 });
  });
  await step('kanban: open new-card editor', async () => {
    const addBtn = page.locator('.kanban-add-card[data-kanban-add="todo"]').first();
    await addBtn.click();
    await page.waitForSelector('#kanban-card-form', { timeout: 5000 });
    const eyebrow = await page.locator('#kanban-card-form .eyebrow').textContent();
    if (/^[a-z][A-Za-z]+$/.test(eyebrow.trim()) && !eyebrow.includes(' ')) throw new Error(`raw i18n key shown: ${eyebrow}`);
  });
  await step('kanban: create card', async () => {
    await page.fill('#kanban-card-title', 'Walkthrough card');
    await page.selectOption('#kanban-card-priority', 'high');
    await page.fill('#kanban-card-due', '2026-09-24');
    await page.click('#kanban-card-form button[type="submit"]');
    await page.waitForSelector('.kanban-card:has-text("Walkthrough card")', { timeout: 10000 });
    await page.screenshot({ path: `${SHOTS}/1-kanban-card-created.png` });
  });
  await step('kanban: edit card via editor', async () => {
    await page.click('.kanban-card:has-text("Walkthrough card")');
    await page.waitForSelector('#kanban-card-form', { timeout: 5000 });
    const val = await page.inputValue('#kanban-card-title');
    if (val !== 'Walkthrough card') throw new Error(`editor not prefilled: "${val}"`);
    await page.fill('#kanban-card-title', 'Walkthrough card v2');
    await page.click('#kanban-card-form button[type="submit"]');
    await page.waitForSelector('.kanban-card:has-text("Walkthrough card v2")', { timeout: 10000 });
    await page.screenshot({ path: `${SHOTS}/2-kanban-card-edited.png` });
  });
  await step('kanban: delete card via editor', async () => {
    await page.click('.kanban-card:has-text("Walkthrough card v2")');
    await page.waitForSelector('#kanban-card-delete', { timeout: 5000 });
    await page.click('#kanban-card-delete');
    await page.waitForSelector('.kanban-card:has-text("Walkthrough card v2")', { state: 'detached', timeout: 10000 });
    await page.screenshot({ path: `${SHOTS}/3-kanban-card-deleted.png` });
  });

  /* ---------- CALENDAR ---------- */
  await step('open calendar', async () => {
    await page.click('[data-view="calendar"]');
    await page.waitForSelector('#calendar-grid .cal-day', { timeout: 10000 });
  });
  await step('calendar: open new-event editor', async () => {
    await page.click('#cal-new-event');
    await page.waitForSelector('#calendar-event-form', { timeout: 5000 });
    const eyebrow = await page.locator('#calendar-event-form .eyebrow').textContent();
    if (/^cal[A-Z]/.test(eyebrow.trim())) throw new Error(`raw i18n key shown: ${eyebrow}`);
  });
  await step('calendar: create event', async () => {
    await page.fill('#cal-event-title', 'Walkthrough event');
    await page.fill('#cal-event-start', '2026-09-25T14:30');
    await page.click('#calendar-event-form button[type="submit"]');
    await page.waitForSelector('.cal-event:has-text("Walkthrough event")', { timeout: 10000 });
    await page.screenshot({ path: `${SHOTS}/4-calendar-event-created.png` });
  });
  await step('calendar: edit event via chip', async () => {
    await page.click('.cal-event:has-text("Walkthrough event")');
    await page.waitForSelector('#calendar-event-form', { timeout: 5000 });
    const val = await page.inputValue('#cal-event-title');
    if (val !== 'Walkthrough event') throw new Error(`editor not prefilled: "${val}"`);
    await page.fill('#cal-event-title', 'Walkthrough event v2');
    await page.click('#calendar-event-form button[type="submit"]');
    await page.waitForSelector('.cal-event:has-text("Walkthrough event v2")', { timeout: 10000 });
    await page.screenshot({ path: `${SHOTS}/5-calendar-event-edited.png` });
  });
  await step('calendar: delete event via editor', async () => {
    await page.click('.cal-event:has-text("Walkthrough event v2")');
    await page.waitForSelector('#cal-event-delete', { timeout: 5000 });
    await page.click('#cal-event-delete');
    await page.waitForSelector('.cal-event:has-text("Walkthrough event v2")', { state: 'detached', timeout: 10000 });
    await page.screenshot({ path: `${SHOTS}/6-calendar-event-deleted.png` });
  });

  console.log('ALL STEPS PASSED');
} catch {
  await page.screenshot({ path: `${SHOTS}/failure-state.png` }).catch(() => {});
  process.exitCode = 1;
} finally {
  console.log(`console errors: ${consoleErrors.length}${consoleErrors.length ? ' :: ' + consoleErrors.slice(0, 5).join(' | ') : ''}`);
  console.log(`page errors: ${pageErrors.length}${pageErrors.length ? ' :: ' + pageErrors.slice(0, 3).join(' | ') : ''}`);
  console.log(`4xx/5xx responses: ${badResponses.length}${badResponses.length ? ' :: ' + badResponses.slice(0, 5).join(' | ') : ''}`);
  await browser.close();
}
