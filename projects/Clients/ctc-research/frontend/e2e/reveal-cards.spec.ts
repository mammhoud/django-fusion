import { expect, test, type Browser, type Page } from '@playwright/test';

/**
 * Reveal-card regression — the `.card.reveal` x-intersect grids, across the
 * three execution modes that previously stranded cards at `opacity: 0`:
 *
 *  1. Normal (JS + Alpine running)  — cards reveal to opacity 1 on scroll.
 *     Guards the backtick `x-intersect='`$el.classList.add(...)`'` bug
 *     (expression evaluated to a string literal, so `reveal-visible` was
 *     never added and every card stayed hidden) and the CSS-specificity bug
 *     where a single-class visible rule lost to a two-class hidden rule.
 *  2. Alpine blocked — the inline head script still adds `.js`, but Alpine
 *     never boots, so `fusion-motion-ready` is never set and the
 *     `html:not(.fusion-motion-ready)` safety net must force the cards
 *     visible. Guards against a missing net stranding content when Alpine
 *     fails to load.
 *  3. No JavaScript — `.js` is never added, so `html:not(.js)` must force
 *     the cards visible. Guards against unconditional `opacity: 0` hidden
 *     states that make content invisible without JS.
 *
 * All assertions check the *computed* opacity rather than Playwright's
 * visibility: `toBeVisible()` ignores `opacity`, so a stuck card would pass
 * a visibility check but fail here.
 *
 * Requires a frontend build that contains the fixes (the net, the corrected
 * x-intersect expressions, and the specificity-bumped visible rules) — the
 * deployed site serves the built artifact, so this spec stays red until the
 * frontend container is rebuilt with the fixes.
 */

const PAGE_PATH = '/features/'; // static `.card.reveal` grid (capabilities)

const CARD = '.card.reveal';

async function assertAllCardsVisible(page: Page): Promise<void> {
  const count = await page.locator(CARD).count();
  expect(count, 'the page should render at least one reveal card').toBeGreaterThan(0);
  for (let i = 0; i < count; i++) {
    const card = page.locator(CARD).nth(i);
    await expect
      .poll(
        () => card.evaluate((node) => getComputedStyle(node).opacity),
        { timeout: 10_000, message: `reveal card ${i + 1}/${count} should be visible (opacity 1)` },
      )
      .toBe('1');
  }
}

test('normal mode: cards reveal to full opacity when scrolled into view', async ({ page }) => {
  await page.goto(PAGE_PATH, { waitUntil: 'commit', timeout: 60_000 });
  // Alpine must actually boot — otherwise this test would pass on the
  // fallback net and no longer exercise the reveal machinery.
  await expect(page.locator('html')).toHaveClass(/fusion-motion-ready/);

  const count = await page.locator(CARD).count();
  expect(count, 'the page should render at least one reveal card').toBeGreaterThan(0);

  for (let i = 0; i < count; i++) {
    const card = page.locator(CARD).nth(i);
    // Center the card in the viewport: `scrollIntoViewIfNeeded` stops as
    // soon as the element touches the viewport edge, which can leave it in
    // the observer's `rootMargin: -40px` dead zone where it never intersects
    // and therefore never reveals.
    await card.evaluate((node) => node.scrollIntoView({ block: 'center' }));
    await expect
      .poll(
        () => card.evaluate((node) => getComputedStyle(node).opacity),
        { timeout: 10_000, message: `reveal card ${i + 1}/${count} should reach opacity 1 on scroll` },
      )
      .toBe('1');
  }
});

test('Alpine blocked: cards stay visible via the fusion-motion-ready net', async ({ page }) => {
  // Block every external script — the inline head script still runs (it adds
  // `.js`), but Alpine's module never loads, so `alpine:init` never fires.
  await page.route('**/*.js', (route) => route.abort());
  await page.goto(PAGE_PATH, { waitUntil: 'commit', timeout: 60_000 });

  // The motion gate must NOT be armed — that is exactly the failure the net
  // protects against.
  await expect(page.locator('html')).toHaveClass(/js/);
  await expect(page.locator('html')).not.toHaveClass(/fusion-motion-ready/);

  // No scrolling needed: `html:not(.fusion-motion-ready)` must force the
  // cards visible immediately.
  await assertAllCardsVisible(page);
});

test('no JavaScript: cards stay visible via the no-JS net', async ({ browser }: { browser: Browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto(PAGE_PATH, { waitUntil: 'commit', timeout: 60_000 });

  await expect(page.locator('html')).not.toHaveClass(/js/);

  await assertAllCardsVisible(page);
  await context.close();
});
