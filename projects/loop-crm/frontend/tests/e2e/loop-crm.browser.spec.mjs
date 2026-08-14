import { test, expect } from '@playwright/test';

const workspaceLabel = 'Playwright workspace';

async function waitForNavigationRefresh(page, href) {
  await page.goto(href);
  await expect(page).toHaveURL(new RegExp(`${href.replaceAll('/', '\\/')}$`));
  await expect(page.locator('#loop-navigation')).toBeVisible();
  await expect(page.locator(`#loop-navigation a[href="${href}"]`)).toHaveAttribute('aria-current', 'page');
}

test.describe('Loop CRM browser interactions', () => {
  test('reloads the complete navigation shell with the correct active state', async ({ page }) => {
    await page.goto('/crm/companies/');
    const shell = page.locator('.loop-shell');
    await expect(shell).toBeVisible();
    await expect(page.locator('#loop-navigation')).toBeVisible();
    await expect(page.locator('#loop-navigation a[href="/crm/companies/"]')).toHaveAttribute('aria-current', 'page');

    await waitForNavigationRefresh(page, '/crm/contacts/');
    await expect(page.locator('#loop-content')).toContainText('Contacts');
    await expect(page.locator('#loop-navigation')).toBeVisible();
    // The active module and its active subpage are both marked, so the
    // hierarchy remains visible to keyboard and screen-reader users.
    await expect(page.locator('#loop-navigation a[aria-current="page"]')).toHaveCount(2);

    await waitForNavigationRefresh(page, '/crm/deals/');
    await expect(page.locator('#loop-content')).toContainText('Deals');
    await expect(page.locator('#loop-navigation a[href="/crm/deals/"]')).toHaveAttribute('aria-current', 'page');
  });

  test('creates, pauses, and queues a workflow through HTMX', async ({ page }, testInfo) => {
    const workflowName = `Browser qualification workflow ${testInfo.workerIndex}-${Date.now()}`;
    await page.goto('/settings/workflows/');
    await expect(page.locator('#workflow-form')).toBeVisible();

    await page.locator('#id_name').fill(workflowName);
    await page.locator('#id_slug').fill(`browser-qualification-${testInfo.workerIndex}-${Date.now()}`);
    await page.locator('#id_description').fill('Created by the browser contract suite.');
    await page.locator('#id_module').selectOption('crm');
    await page.locator('#id_trigger').fill('contact.created');
    await page.locator('#id_actions').fill('["assign_owner", "notify_sales"]');
    await page.locator('#workflow-form button[type="submit"]').click();
    const created = page.locator('#workflow-list').getByText(workflowName).first();
    await expect(created).toBeVisible();

    const row = page.locator('.loop-workflow-row').filter({ hasText: workflowName }).first();
    await row.getByRole('button', { name: 'Activate' }).click();
    await expect(row).toContainText('Active');
    await expect(row.getByRole('button', { name: 'Pause' })).toBeVisible();

    await row.getByRole('button', { name: 'Queue run' }).click();
    await expect(page.locator('#workflow-runs')).toContainText('Browser qualification workflow');
    await expect(page.locator('#workflow-runs')).toContainText(/Queued|Running|Succeeded|Failed/);
  });

  test('creates a draft and advances content through review and scheduling', async ({ page }, testInfo) => {
    const postContent = `Browser-created content review checkpoint ${testInfo.workerIndex}-${Date.now()}.`;
    await page.goto('/marketing/calendar/');
    await expect(page.locator('#post-form')).toBeVisible();
    await expect(page.locator('#id_workspace')).toContainText(workspaceLabel);

    await page.locator('#id_workspace').selectOption({ label: workspaceLabel });
    await page.locator('#id_channel').selectOption({ label: 'LinkedIn — Playwright channel' });
    await page.locator('#id_content').fill(postContent);
    await page.locator('#id_scheduled_at').fill('2026-10-16T10:30');
    await page.locator('#post-form button[type="submit"]').click();

    const post = page.locator('.loop-post-row').filter({ hasText: postContent }).first();
    await expect(post).toContainText('Draft');
    await post.getByRole('button', { name: 'Submit' }).click();
    await expect(post).toContainText('Pending approval');
    await post.getByRole('button', { name: 'Approve' }).click();
    await expect(post).toContainText('Approved');
    await post.getByRole('button', { name: 'Schedule' }).click();
    await expect(post).toContainText('Scheduled');
  });
});
