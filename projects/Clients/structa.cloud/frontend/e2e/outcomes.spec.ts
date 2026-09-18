import { expect, test } from '@playwright/test';

test('homepage explains outcomes and gives buyers a clear next step', async ({ page }) => {
  const response = await page.goto('/');
  expect(response?.status()).toBe(200);
  await expect(page.locator('#outcomes-heading')).toBeVisible();
  await expect(page.locator('[data-outcome-service]').first()).toBeVisible();
  await expect(page.locator('[data-roi-model]')).toBeVisible();
  await expect(page.locator('[data-assessment-cta]')).toHaveAttribute('href', /topic=infrastructure-and-ai-assessment/);
});

test('homepage ROI model responds to user inputs', async ({ page }) => {
  await page.goto('/');
  const people = page.locator('[data-roi-model] input[type="number"]').nth(0);
  await expect(people).toBeVisible();
  await people.fill('10');
  await expect(page.locator('[data-roi-output]')).toHaveText('$176,800');
});

test('assessment CTA preselects and submits a valid contact topic', async ({ page }) => {
  await page.goto('/contact/?topic=infrastructure-and-ai-assessment');
  const topic = page.locator('#cf-topic');
  await expect(topic).toHaveValue('infrastructure-and-ai-assessment');
  await expect(page.locator('#cf-subject')).toHaveValue('Free infrastructure, AI, and automation assessment');
  await page.locator('#cf-name').fill('Test visitor');
  await page.locator('#cf-email').fill('test@example.com');
  await page.locator('#cf-message').fill('I would like to understand our first automation opportunity.');

  let submitted: Record<string, string> | undefined;
  await page.route(/\/fragment\/contact(?:\/|$)/, async (route) => {
    submitted = JSON.parse(route.request().postData() || '{}');
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true }) });
  });
  await page.getByRole('button', { name: /send message/i }).click({ force: true });
  await expect.poll(() => submitted?.topic, { timeout: 10000 }).toBe('infrastructure-and-ai-assessment');
  expect(submitted?.subject).toBe('Free infrastructure, AI, and automation assessment');
  await expect(page.locator('h3').filter({ hasText: /send us a message/i })).toBeVisible();
});
