import { expect, test } from '@playwright/test';
import { BACKEND_URL } from '../playwright.config';

test('profile shell renders a useful signed-out state', async ({ page }) => {
  const response = await page.goto('/profile/');
  expect(response?.status()).toBe(200);
  await expect(page.locator('h1')).toContainText(/profile/i);
  await expect(page.getByText(/sign in to see your progress|sign in to view your profile/i)).toBeVisible();
});

test('profile settings remains a backend-owned auth route', async ({ request }) => {
  const response = await request.get(`${BACKEND_URL}/profile/settings/`, { maxRedirects: 0 });
  expect([200, 302, 303]).toContain(response.status());
  expect(response.status()).not.toBe(404);
});

test('seeded blog detail renders the article and moderated comments surface', async ({ page }) => {
  const response = await page.goto('/blog/why-landing-pages-as-documents/');
  expect(response?.status()).toBe(200);
  await expect(page.locator('h1').first()).toBeVisible();
  await expect(page.getByText('Comments', { exact: true })).toBeVisible();
  await expect(page.getByText(/sign in to join the conversation|leave a comment/i)).toBeVisible();
});
