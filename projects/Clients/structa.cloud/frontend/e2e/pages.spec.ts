import { expect, test } from '@playwright/test';

/**
 * Static content pages — every public route serves 200 with a heading.
 * Patterns match the live copy; `null` falls back to a non-empty h1.
 */
const PAGES: Array<[string, RegExp | null]> = [
  ['/about/', null], // hero: "A clearer path to market"
  ['/blog/', null], // hero: "Ideas from real launches"
  ['/pricing/', /pricing/i],
  ['/services/benefits/', null], // hero: "Built to ship as…"
  ['/products/', null], // hero: "Most of what we build, shipped as…"
  ['/services/', null], // hero: "From idea to market"
  ['/faq/', /faq|question/i],
  ['/contact/', null], // "We'd love to hear from you"
  ['/privacy/', /privacy/i],
  ['/brand/', null], // hero: "One family, six marks"
  ['/profile/', /profile/i],
];

for (const [path, headingPattern] of PAGES) {
  test(`page ${path} renders 200 with a heading`, async ({ page }) => {
    const response = await page.goto(path);
    expect(response?.status(), `${path} should be 200`).toBe(200);
    const h1 = (await page.locator('h1').first().textContent())?.trim() || '';
    expect(h1.length, `${path} should have a non-empty h1`).toBeGreaterThan(3);
    if (headingPattern) {
      expect(h1, `${path} h1 should match ${headingPattern}`).toMatch(headingPattern);
    }
  });
}
