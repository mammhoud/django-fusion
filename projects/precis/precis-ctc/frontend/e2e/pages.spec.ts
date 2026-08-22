import { expect, test } from '@playwright/test';

/**
 * Static content pages — every public route serves 200 with a heading.
 * Patterns match the live copy; `null` falls back to a non-empty h1.
 */
const PAGES: Array<[string, RegExp | null]> = [
  ['/', /clinical|research|evidence/i],
  ['/about/', /about|research/i],
  ['/about/founder/', /founder|built by/i],
  ['/about/research/', /research|checked/i],
  ['/about/education/', /learn|education/i],
  ['/blog/', /blog|insight/i],
  ['/pricing/', /pricing/i],
  ['/features/', /documents|capabilit/i],
  ['/products/', /program|product/i],
  ['/services/', /capabilit|research|service/i],
  ['/team/', /innovator|team|network/i],
  ['/events/', /event|research/i],
  ['/faq/', /faq|question/i],
  ['/contact/', /contact|research/i],
  ['/privacy/', /privacy|policy/i],
  ['/documents/', /document|research/i],
  ['/projects/', /program|project/i],
  ['/profile/', /profile|learning/i],
  ['/blog/medical-ai-clinical-evidence-limits/', /medical ai|blog/i],
];

for (const [path, headingPattern] of PAGES) {
  test(`page ${path} renders 200 with a heading`, async ({ page }) => {
    const response = await page.goto(path, { waitUntil: 'domcontentloaded' });
    expect(response?.status(), `${path} should be 200`).toBe(200);
    const h1 = (await page.locator('h1').first().textContent())?.trim() || '';
    expect(h1.length, `${path} should have a non-empty h1`).toBeGreaterThan(3);
    if (headingPattern) {
      expect(h1, `${path} h1 should match ${headingPattern}`).toMatch(headingPattern);
    }
  });
}
